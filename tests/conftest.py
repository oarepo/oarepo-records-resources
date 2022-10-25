import pytest
from flask_security import login_user
from invenio_access import current_access, ActionUsers
from flask_security.utils import hash_password
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from invenio_records_resources.services.uow import UnitOfWork, RecordCommitOp

#from model_document.proxies import current_service as document_service
from model_document.records.api import ModelDocumentRecord
from model_document.services.config import ModelDocumentServiceConfig

from model_file.proxies import current_service as file_service
from model_file.records.api import ModelFileRecord


from invenio_records_resources.services import RecordService as InvenioRecordService

from oarepo_records_resources.services.expandable_fields import ReferencedRecordExpandableField


class ModelDocumentService(InvenioRecordService):
    @property
    def expandable_fields(self):
        return [
            ReferencedRecordExpandableField(field_name="metadata.file",
                                            keys=["metadata.filename", "metadata.filesize"],
                                            service=file_service),
        ]



@pytest.fixture(scope="module")
def document_service():
    return ModelDocumentService(ModelDocumentServiceConfig())

@pytest.fixture(scope="function")
def sample_document_dict(sample_file_record):
    return {"metadata": {
                     "title": "record 1",
                     "file": {"id": sample_file_record["id"]}
                 }}


@pytest.fixture(scope="module")
def sample_file_dict():
    ret = {"metadata": {
        "filename": "record 1 - file 1",
        "licence_type": "blabla",
        "filesize": 512}
    }
    return ret


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config["RATELIMIT_AUTHENTICATED_USER"] = "200 per second"
    return app_config


@pytest.fixture(scope="function")
def sample_document_record(app, db, sample_file_record, sample_document_dict, document_service):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelDocumentRecord.create(sample_document_dict)
        uow.register(RecordCommitOp(record, document_service.indexer, True))
        uow.commit()
        return record


@pytest.fixture(scope="function")
def sample_file_record(app, db, sample_file_dict):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelFileRecord.create(sample_file_dict)
        uow.register(RecordCommitOp(record, file_service.indexer, True))
        uow.commit()
        return record


@pytest.fixture()
def user(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        _user = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
    db.session.commit()
    return _user


@pytest.fixture()
def role(app, db):
    """Create some roles."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role = datastore.create_role(name="admin", description="admin role")

    db.session.commit()
    return role


@pytest.fixture()
def client_with_credentials(db, client, user, role):
    """Log in a user to the client."""

    current_datastore.add_role_to_user(user, role)
    action = current_access.actions["superuser-access"]
    db.session.add(ActionUsers.allow(action, user_id=user.id))

    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)

    return client