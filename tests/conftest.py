import os

import pytest
from flask_security import login_user
from invenio_access import current_access, ActionUsers
from flask_security.utils import hash_password
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from invenio_records_resources.services.uow import UnitOfWork, RecordCommitOp

from model_document_picture.records.api import ModelDocumentPictureRecord
from model_document_picture.services.records.config import ModelDocumentPictureServiceConfig
from model_document_picture.services.records.service import ModelDocumentPictureService

from model_document_no_expandable_fields.records.api import ModelDocumentNoExpandableFieldsRecord
from model_document_no_expandable_fields.services.records.config import ModelDocumentNoExpandableFieldsServiceConfig
from model_document_no_expandable_fields.services.records.service import ModelDocumentNoExpandableFieldsService

from model_file.proxies import current_service as file_service
from model_file.records.api import ModelFileRecord

from model_picture.proxies import current_service as picture_service
from model_picture.records.api import ModelPictureRecord

from model_document.records.api import ModelDocumentRecord
from model_document.services.records.config import ModelDocumentServiceConfig
from model_document.services.records.service import ModelDocumentService


@pytest.fixture(scope="module")
def document_service():
    return ModelDocumentService(ModelDocumentServiceConfig())

@pytest.fixture(scope="module")
def document_no_expandable_fields_service():
    return ModelDocumentNoExpandableFieldsService(ModelDocumentNoExpandableFieldsServiceConfig())

@pytest.fixture(scope="module")
def document_picture_service():
    return ModelDocumentPictureService(ModelDocumentPictureServiceConfig())

@pytest.fixture(scope="function")
def sample_document_dict(sample_file_record):
    return {"metadata": {
                     "title": "record 1",
                     "file": {"id": sample_file_record["id"]}
                 }}

#todo alt id is just to test whether the custome choice of pid_fields works
@pytest.fixture(scope="function")
def sample_document_dict(sample_file_record, sample_picture_record):
    return {"metadata": {
                     "title": "record 1",
                     "file": {"id": sample_file_record["id"]},
                     "picture": {"alt_id": sample_picture_record["id"]}
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
def sample_picture_dict():
    ret = {"metadata": {
        "filename": "picture 1",
        "alt": "blabla",
        "alt_id": 1}
    }
    return ret


@pytest.fixture(scope="function")
def sample_file_record(app, db, sample_file_dict):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelFileRecord.create(sample_file_dict)
        uow.register(RecordCommitOp(record, file_service.indexer, True))
        uow.commit()
        return record

@pytest.fixture(scope="function")
def sample_picture_record(app, db, sample_picture_dict):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelPictureRecord.create(sample_picture_dict)
        uow.register(RecordCommitOp(record, picture_service.indexer, True))
        uow.commit()
        return record

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
def sample_document_no_expand_record(app, db, sample_file_record, sample_document_dict, document_service):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelDocumentNoExpandableFieldsRecord.create(sample_document_dict)
        uow.register(RecordCommitOp(record, document_service.indexer, True))
        uow.commit()
        return record

@pytest.fixture(scope="function")
def sample_document_picture_record(app, db, sample_file_record, sample_document_dict, document_picture_service):
    # record = current_service.create(system_identity, sample_data[0])
    # return record
    with UnitOfWork(db.session) as uow:
        record = ModelDocumentPictureRecord.create(sample_document_dict)
        uow.register(RecordCommitOp(record, document_picture_service.indexer, True))
        uow.commit()
        return record




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
    app_config["SEARCH_HOSTS"] = [
        {
            "host": os.environ.get("OPENSEARCH_HOST", "localhost"),
            "port": os.environ.get("OPENSEARCH_PORT", "9200"),
        }
    ]
    return app_config

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