from __future__ import annotations

from app.utils.filename_parser import parse_filename
from app.utils.filename_types import ParsedFile


def _assert_parsed(
    result: ParsedFile,
    *,
    display_name: str | None = None,
    quality: str | None = None,
    languages: list[str] | None = None,
    season: str | None = None,
    episode: str | None = None,
    episode_end: str | None = None,
    missing_quality: bool = False,
    missing_language: bool = False,
    original_filename: str = "",
) -> None:
    if original_filename:
        assert result.original_filename == original_filename
    if display_name is not None:
        assert result.display_name == display_name, (
            f"display_name mismatch: {result.display_name!r} != {display_name!r}"
        )
    if quality is not None:
        assert result.quality == quality
    if languages is not None:
        assert result.languages == languages
    if season is not None:
        assert result.season == season
    if episode is not None:
        assert result.episode == episode
    if episode_end is not None:
        assert result.episode_end == episode_end
    assert result.missing_quality == missing_quality
    assert result.missing_language == missing_language


# ── Movies ──────────────────────────────────────────────────────────────────


def test_movie_hindi() -> None:
    r = parse_filename("Avengers.Endgame.2019.1080p.BluRay.Hindi.mkv")
    _assert_parsed(
        r,
        original_filename="Avengers.Endgame.2019.1080p.BluRay.Hindi.mkv",
        display_name="\U0001F3AC 1080p \u2022 Hindi",
        quality="1080p",
        languages=["Hindi"],
    )


def test_movie_4k_dual_audio() -> None:
    r = parse_filename("Avatar.2009.2160p.Dual.Audio.mkv")
    _assert_parsed(
        r,
        original_filename="Avatar.2009.2160p.Dual.Audio.mkv",
        display_name="\U0001F3AC 4K \u2022 Dual Audio",
        quality="4K",
        languages=["Dual Audio"],
    )


def test_movie_hindi_abbreviation() -> None:
    r = parse_filename("Pushpa.2025.1080p.Hin.Eng.mkv")
    _assert_parsed(
        r,
        original_filename="Pushpa.2025.1080p.Hin.Eng.mkv",
        display_name="\U0001F3AC 1080p \u2022 Hindi + English",
        quality="1080p",
        languages=["Hindi", "English"],
    )


def test_movie_multi_audio() -> None:
    r = parse_filename("Jailer.2024.1080p.Multi.mkv")
    _assert_parsed(
        r,
        original_filename="Jailer.2024.1080p.Multi.mkv",
        display_name="\U0001F3AC 1080p \u2022 Multi Audio",
        quality="1080p",
        languages=["Multi Audio"],
    )


def test_movie_three_languages_becomes_multi_audio() -> None:
    r = parse_filename("Movie.2023.1080p.Hin.Eng.Tam.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["Hindi", "English", "Tamil"],
        missing_quality=False,
        missing_language=False,
    )
    assert "Multi Audio" in r.display_name
    assert "Hindi" not in r.display_name


def test_movie_uhd_normalized_to_4k() -> None:
    r = parse_filename("Movie.2023.UHD.English.mkv")
    _assert_parsed(r, quality="4K", languages=["English"])


def test_movie_4k_normalized() -> None:
    r = parse_filename("Movie.2023.4K.Hindi.mkv")
    _assert_parsed(r, quality="4K", languages=["Hindi"])


def test_movie_tamil() -> None:
    r = parse_filename("Movie.2024.1080p.Tamil.mkv")
    _assert_parsed(r, quality="1080p", languages=["Tamil"])


def test_movie_telugu_abbreviation() -> None:
    r = parse_filename("Movie.2024.1080p.Tel.mkv")
    _assert_parsed(r, quality="1080p", languages=["Telugu"])


def test_movie_malayalam_abbreviation() -> None:
    r = parse_filename("Movie.2024.1080p.Mal.mkv")
    _assert_parsed(r, quality="1080p", languages=["Malayalam"])


def test_movie_turkish() -> None:
    r = parse_filename("Movie.2024.1080p.Turkish.mkv")
    _assert_parsed(r, quality="1080p", languages=["Turkish"])


def test_movie_turkish_abbreviation() -> None:
    r = parse_filename("Movie.2024.1080p.Tur.mkv")
    _assert_parsed(r, quality="1080p", languages=["Turkish"])


# ── Quality levels ──────────────────────────────────────────────────────────


def test_quality_240p() -> None:
    r = parse_filename("Movie.240p.Hindi.mkv")
    _assert_parsed(r, quality="240p", languages=["Hindi"])


def test_quality_360p() -> None:
    r = parse_filename("Movie.360p.English.mkv")
    _assert_parsed(r, quality="360p", languages=["English"])


def test_quality_480p() -> None:
    r = parse_filename("Movie.480p.Hindi.mkv")
    _assert_parsed(r, quality="480p", languages=["Hindi"])


def test_quality_576p() -> None:
    r = parse_filename("Movie.576p.English.mkv")
    _assert_parsed(r, quality="576p", languages=["English"])


def test_quality_720p() -> None:
    r = parse_filename("Movie.720p.Hindi.mkv")
    _assert_parsed(r, quality="720p", languages=["Hindi"])


def test_quality_1080p() -> None:
    r = parse_filename("Movie.1080p.English.mkv")
    _assert_parsed(r, quality="1080p", languages=["English"])


def test_quality_1440p() -> None:
    r = parse_filename("Movie.1440p.Hindi.mkv")
    _assert_parsed(r, quality="1440p", languages=["Hindi"])


def test_quality_2160p() -> None:
    r = parse_filename("Movie.2160p.English.mkv")
    _assert_parsed(r, quality="4K", languages=["English"])


def test_quality_4320p() -> None:
    r = parse_filename("Movie.4320p.Hindi.mkv")
    _assert_parsed(r, quality="8K", languages=["Hindi"])


# ── Series / TV Shows ───────────────────────────────────────────────────────


def test_series_sxxexx() -> None:
    r = parse_filename("Money.Heist.S03E05.720p.Tel.mkv")
    _assert_parsed(
        r,
        original_filename="Money.Heist.S03E05.720p.Tel.mkv",
        display_name="\U0001F3AC S03E05 \u2022 720p \u2022 Telugu",
        quality="720p",
        languages=["Telugu"],
        season="03",
        episode="05",
    )


def test_series_sxex_short() -> None:
    r = parse_filename("Show.S1E5.1080p.English.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["English"],
        season="01",
        episode="05",
    )


def test_series_season_spelled_out() -> None:
    r = parse_filename("Show.Season 1 Episode 2.1080p.English.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["English"],
        season="01",
        episode="02",
    )


def test_series_sxx_ep_style() -> None:
    r = parse_filename("Show.S01.EP.05.1080p.English.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["English"],
        season="01",
        episode="05",
    )


# ── Combined episodes (range) ────────────────────────────────────────────────


def test_combined_episodes_hyphen() -> None:
    r = parse_filename("Show.S01.EP.21-24.1080p.Hindi.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["Hindi"],
        season="01",
        episode="21",
        episode_end="24",
    )


def test_combined_episodes_spaces() -> None:
    r = parse_filename("Show.S01 EP 21-24.1080p.Hindi.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=["Hindi"],
        season="01",
        episode="21",
        episode_end="24",
    )


# ── Dual Audio variants ─────────────────────────────────────────────────────


def test_dual_audio_separate_words() -> None:
    r = parse_filename("Movie.2023.1080p.Dual.Audio.mkv")
    _assert_parsed(r, quality="1080p", languages=["Dual Audio"])


def test_dual_audio_combined() -> None:
    r = parse_filename("Movie.2023.1080p.DualAudio.mkv")
    _assert_parsed(r, quality="1080p", languages=["Dual Audio"])


def test_dual_audio_hyphenated() -> None:
    r = parse_filename("Movie.2023.1080p.Dual-Audio.mkv")
    _assert_parsed(r, quality="1080p", languages=["Dual Audio"])


# ── Multi Audio variants ────────────────────────────────────────────────────


def test_multi_audio_separate_words() -> None:
    r = parse_filename("Movie.2023.720p.Multi.Audio.mkv")
    _assert_parsed(r, quality="720p", languages=["Multi Audio"])


def test_multi_audio_combined() -> None:
    r = parse_filename("Movie.2023.720p.MultiAudio.mkv")
    _assert_parsed(r, quality="720p", languages=["Multi Audio"])


def test_multi_audio_hyphenated() -> None:
    r = parse_filename("Movie.2023.720p.Multi-Audio.mkv")
    _assert_parsed(r, quality="720p", languages=["Multi Audio"])


# ── Missing fields (flags, not rejection) ───────────────────────────────────


def test_missing_language() -> None:
    r = parse_filename("Movie.1080p.mkv")
    _assert_parsed(
        r,
        quality="1080p",
        languages=[],
        missing_quality=False,
        missing_language=True,
    )
    assert "\U0001F937" in r.display_name


def test_missing_quality() -> None:
    r = parse_filename("Movie.Hindi.mkv")
    _assert_parsed(
        r,
        quality=None,
        languages=["Hindi"],
        missing_quality=True,
        missing_language=False,
    )
    assert "\U0001F937" in r.display_name


def test_missing_both() -> None:
    r = parse_filename("Movie.mkv")
    _assert_parsed(
        r,
        quality=None,
        languages=[],
        missing_quality=True,
        missing_language=True,
    )
    assert "\U0001F937" in r.display_name


# ── Preserve original ───────────────────────────────────────────────────────


def test_preserves_original_filename() -> None:
    r = parse_filename("My.Movie.2023.1080p.Hindi.mkv")
    assert r.original_filename == "My.Movie.2023.1080p.Hindi.mkv"
    assert r.display_name != r.original_filename


def test_parsed_file_fields() -> None:
    r = parse_filename("Test.2023.1080p.English.mkv")
    assert r.file_id is None
    assert r.file_unique_id is None
    assert r.file_size == 0
    assert r.mime_type is None


# ── Real filenames from project samples ─────────────────────────────────────


def test_real_filename_1() -> None:
    r = parse_filename("Avengers.Endgame.2019.1080p.BluRay.Hin.Eng.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi", "English"]


def test_real_filename_2() -> None:
    r = parse_filename("The.Matrix.Resurrections.2021.2160p.WEB-DL.DD5.1.Hin.Eng.mkv")
    assert r.quality == "4K"
    assert "Hindi" in r.languages
    assert "English" in r.languages


def test_real_filename_3() -> None:
    r = parse_filename("RRR.2022.1080p.WEB-DL.DD5.1.Hin.Tam.Tel.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi", "Tamil", "Telugu"]
    assert "Multi Audio" in r.display_name


def test_real_filename_4() -> None:
    r = parse_filename("Game.of.Thrones.S01E05.1080p.BluRay.Eng.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["English"]
    assert r.season == "01"
    assert r.episode == "05"
