from reuse_my_code.models import SearchRequest
from reuse_my_code.registry import load_registry, search_capabilities, validate_registry_consistency


def test_registry_declares_existing_files_and_required_fields():
    assert validate_registry_consistency() == []


def test_every_registry_entry_is_searchable_by_its_primary_capability():
    for item in load_registry():
        result = search_capabilities(
            SearchRequest(
                capability=item["capability"],
                language=item["language"],
                framework=item["framework"],
            )
        )
        assert any(match.asset_id == item["asset_id"] for match in result.matches)
