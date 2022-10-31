#from model_document.proxies import current_service as document_service
from invenio_access.permissions import system_identity


def test_expandable_fields(sample_file_record, sample_document_record, sample_document_dict, sample_file_dict,
                           document_service, document_no_expandable_fields_service, sample_document_no_expand_record,
                           sample_document_picture_record, document_picture_service, sample_picture_record):

    expected_expanded_file = {
        "metadata":
            {
                "filename": "record 1 - file 1",
                "filesize": 512
            }
    }
    expected_expanded_picture = {
        "metadata":
            {
                "alt": "blabla"
            }
    }
    #one expandable field
    doc_id = sample_document_record["id"]
    r = document_service.read(system_identity, doc_id, expand=True)
    data = r.data
    expanded = data["expanded"]["metadata"]["file"]

    assert len(data["expanded"]) == 1
    assert len(data["expanded"]["metadata"]) == 1
    assert expanded == expected_expanded_file

    #two expandable fields
    doc_id = sample_document_picture_record["id"]
    r = document_picture_service.read(system_identity, doc_id, expand=True)
    data = r.data
    assert len(data["expanded"]) == 1
    assert len(data["expanded"]["metadata"]) == 2
    expanded_file = data["expanded"]["metadata"]["file"]
    expanded_picture = data["expanded"]["metadata"]["picture"]
    assert expanded_file == expected_expanded_file
    assert expanded_picture == expected_expanded_picture

    print()


    doc_id = sample_document_no_expand_record["id"]
    r = document_no_expandable_fields_service.read(system_identity, doc_id, expand=True)
    data = r.data
    assert data["expanded"] == {}
    #assert expanded["id"] == doc_id