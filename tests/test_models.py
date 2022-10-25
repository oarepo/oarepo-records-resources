#from model_document.proxies import current_service as document_service
from invenio_access.permissions import system_identity


def test_expandable_fields(sample_file_record, sample_document_record, sample_document_dict, sample_file_dict,
                           document_service):

    doc_id = sample_document_record["id"]
    r = document_service.read(system_identity, doc_id, expand=True)

    data = r.data
    expanded = data["expanded"]["metadata"]["file"]
    assert len(expanded["metadata"]) == 2
    assert expanded["metadata"]["filename"] == sample_file_dict["metadata"]["filename"]
    assert expanded["metadata"]["filesize"] == sample_file_dict["metadata"]["filesize"]
    #assert expanded["id"] == doc_id