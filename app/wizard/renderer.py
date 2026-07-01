from app.ui.icons import Icons
from app.wizard.core import WizardContext, WizardStep

BAR_FULL = "█"
BAR_EMPTY = "░"
BAR_LENGTH = 10


def _progress_bar(step: int, total: int) -> str:
    fraction = step / total if total else 0
    filled = round(fraction * BAR_LENGTH)
    bar = BAR_FULL * filled + BAR_EMPTY * (BAR_LENGTH - filled)
    pct = round(fraction * 100)
    return f"{bar} {pct}%"


def _is_set(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (list, tuple)) and not value:
        return False
    return True


def _field_summary(steps: list[WizardStep], context: WizardContext) -> str:
    lines: list[str] = []
    for s in steps:
        if not s.field_name:
            continue
        value = getattr(context, s.field_name, None)
        val_str = s.render_summary_value(context)
        display = val_str if val_str else s.title
        if _is_set(value):
            lines.append(f"{Icons.SUCCESS} {display}")
        else:
            lines.append(f"{Icons.INFO} {display}")
    return "\n".join(lines)


def render_wizard_screen(
    title: str,
    step: int,
    total: int,
    steps: list[WizardStep],
    context: WizardContext,
    prompt: str,
    error: str | None = None,
) -> str:
    lines: list[str] = [
        f"{Icons.UPLOAD} <b>{title}</b>",
        "",
        f"Step {step}/{total}  {_progress_bar(step, total)}",
        "",
        "━━━━━━━━━━━━━━━━",
        _field_summary(steps, context),
        "━━━━━━━━━━━━━━━━",
    ]

    if error:
        lines.extend([
            "",
            f"{Icons.WARNING} {error}",
        ])

    lines.extend([
        "",
        prompt,
    ])

    return "\n".join(lines)
