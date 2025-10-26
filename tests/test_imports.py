"""Simple smoke tests ensuring key modules import without errors."""

def test_import_core_modules():
    import core.data_logic  # noqa: F401
    import core.data_loader  # noqa: F401
    import core.datasource  # noqa: F401
    import core.task_logic  # noqa: F401


def test_import_ui_modules():
    import ui.expanders  # noqa: F401
    import ui.hero_cards  # noqa: F401
    import ui.sections  # noqa: F401
    import ui.refresh_controls  # noqa: F401
    import ui.unit_cards  # noqa: F401


def test_import_utils_modules():
    import utils.helpers  # noqa: F401
    import utils.styling  # noqa: F401
    import utils.logger  # noqa: F401
