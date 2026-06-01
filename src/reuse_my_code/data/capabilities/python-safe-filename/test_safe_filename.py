from app.services.safe_filename import make_safe_filename


def test_strips_path_components_and_keeps_extension():
    name = make_safe_filename("../../avatar.png")
    assert "/" not in name
    assert ".." not in name
    assert name.endswith(".png")


def test_generates_unique_names():
    assert make_safe_filename("a.png") != make_safe_filename("a.png")
