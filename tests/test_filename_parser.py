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
            f"display_name mismatch:\n  got:      {result.display_name!r}\n  expected: {display_name!r}"
        )
    if quality is not None:
        assert result.quality == quality, f"quality mismatch: {result.quality!r} != {quality!r}"
    if languages is not None:
        assert result.languages == languages, f"languages mismatch: {result.languages!r} != {languages!r}"
    if season is not None:
        assert result.season == season
    if episode is not None:
        assert result.episode == episode
    if episode_end is not None:
        assert result.episode_end == episode_end
    assert result.missing_quality == missing_quality
    assert result.missing_language == missing_language


def _assert_missing(result: ParsedFile, *, quality: bool = False, language: bool = False) -> None:
    assert result.missing_quality == quality
    assert result.missing_language == language


# ══════════════════════════════════════════════════════════════════════════════
# 1. MOVIES (from spec examples)
# ══════════════════════════════════════════════════════════════════════════════

def test_movie_avengers_hindi() -> None:
    r = parse_filename("Avengers.Endgame.2019.1080p.BluRay.Hindi.mkv")
    _assert_parsed(r,
        original_filename="Avengers.Endgame.2019.1080p.BluRay.Hindi.mkv",
        display_name="\U0001F3AC 1080p \u2022 Hindi",
        quality="1080p", languages=["Hindi"])

def test_movie_avengers_eng() -> None:
    r = parse_filename("Avengers.Endgame.2019.720p.Eng.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC 720p \u2022 English",
        quality="720p", languages=["English"])

def test_movie_avatar_4k_dual() -> None:
    r = parse_filename("Avatar.2009.2160p.Dual.Audio.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC 4K \u2022 Dual Audio",
        quality="4K", languages=["Dual Audio"])

def test_movie_pushpa_hin_eng() -> None:
    r = parse_filename("Pushpa.2025.1080p.Hin.Eng.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC 1080p \u2022 Hindi + English",
        quality="1080p", languages=["Hindi", "English"])

def test_movie_leo_4k_tam() -> None:
    r = parse_filename("Leo.2025.4K.Tam.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC 4K \u2022 Tamil",
        quality="4K", languages=["Tamil"])


# ══════════════════════════════════════════════════════════════════════════════
# 2. TV SHOWS (from spec examples)
# ══════════════════════════════════════════════════════════════════════════════

def test_tv_money_heist() -> None:
    r = parse_filename("Money.Heist.S03E05.1080p.English.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC S03E05 \u2022 1080p \u2022 English",
        quality="1080p", languages=["English"], season="03", episode="05")

def test_tv_rafta_hin_tur() -> None:
    r = parse_filename("Arafta.S01E73.1080p.AMZN.WEB-DL.Hin.Tur.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC S01E73 \u2022 1080p \u2022 Hindi + Turkish",
        quality="1080p", languages=["Hindi", "Turkish"], season="01", episode="73")

def test_tv_combined_episodes_multi_audio() -> None:
    r = parse_filename("S01 EP 21-24 COMBiNED TRUE WEB-DL 720p Tam Tel Hin Mal Kan.mkv")
    _assert_parsed(r,
        display_name="\U0001F3AC S01 \u2022 EP21\u201324 \u2022 720p \u2022 Multi Audio",
        quality="720p", languages=["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"],
        season="01", episode="21", episode_end="24")


# ══════════════════════════════════════════════════════════════════════════════
# 3. LANGUAGE ABBREVIATIONS — all variants
# ══════════════════════════════════════════════════════════════════════════════

def test_lang_hin() -> None:
    assert parse_filename("M.1080p.Hin.mkv").languages == ["Hindi"]

def test_lang_hindi() -> None:
    assert parse_filename("M.1080p.Hindi.mkv").languages == ["Hindi"]

def test_lang_hin_upper() -> None:
    assert parse_filename("M.1080p.HIN.mkv").languages == ["Hindi"]

def test_lang_eng() -> None:
    assert parse_filename("M.1080p.Eng.mkv").languages == ["English"]

def test_lang_english() -> None:
    assert parse_filename("M.1080p.English.mkv").languages == ["English"]

def test_lang_eng_upper() -> None:
    assert parse_filename("M.1080p.ENG.mkv").languages == ["English"]

def test_lang_tam() -> None:
    assert parse_filename("M.1080p.Tam.mkv").languages == ["Tamil"]

def test_lang_tamil() -> None:
    assert parse_filename("M.1080p.Tamil.mkv").languages == ["Tamil"]

def test_lang_tam_upper() -> None:
    assert parse_filename("M.1080p.TAM.mkv").languages == ["Tamil"]

def test_lang_tel() -> None:
    assert parse_filename("M.1080p.Tel.mkv").languages == ["Telugu"]

def test_lang_telugu() -> None:
    assert parse_filename("M.1080p.Telugu.mkv").languages == ["Telugu"]

def test_lang_tel_upper() -> None:
    assert parse_filename("M.1080p.TEL.mkv").languages == ["Telugu"]

def test_lang_mal() -> None:
    assert parse_filename("M.1080p.Mal.mkv").languages == ["Malayalam"]

def test_lang_malayalam() -> None:
    assert parse_filename("M.1080p.Malayalam.mkv").languages == ["Malayalam"]

def test_lang_kan() -> None:
    assert parse_filename("M.1080p.Kan.mkv").languages == ["Kannada"]

def test_lang_kannada() -> None:
    assert parse_filename("M.1080p.Kannada.mkv").languages == ["Kannada"]

def test_lang_tur() -> None:
    assert parse_filename("M.1080p.Tur.mkv").languages == ["Turkish"]

def test_lang_turkish() -> None:
    assert parse_filename("M.1080p.Turkish.mkv").languages == ["Turkish"]

def test_lang_tur_upper() -> None:
    assert parse_filename("M.1080p.TUR.mkv").languages == ["Turkish"]

def test_lang_jp() -> None:
    assert parse_filename("M.1080p.JP.mkv").languages == ["Japanese"]

def test_lang_jap() -> None:
    assert parse_filename("M.1080p.Jap.mkv").languages == ["Japanese"]

def test_lang_kor() -> None:
    assert parse_filename("M.1080p.Kor.mkv").languages == ["Korean"]

def test_lang_chi() -> None:
    assert parse_filename("M.1080p.Chi.mkv").languages == ["Chinese"]

def test_lang_spa() -> None:
    assert parse_filename("M.1080p.Spa.mkv").languages == ["Spanish"]

def test_lang_fre() -> None:
    assert parse_filename("M.1080p.Fre.mkv").languages == ["French"]

def test_lang_fr() -> None:
    assert parse_filename("M.1080p.Fr.mkv").languages == ["French"]

def test_lang_ger() -> None:
    assert parse_filename("M.1080p.Ger.mkv").languages == ["German"]

def test_lang_de() -> None:
    assert parse_filename("M.1080p.De.mkv").languages == ["German"]


# ══════════════════════════════════════════════════════════════════════════════
# 4. SEPARATORS
# ══════════════════════════════════════════════════════════════════════════════

def test_sep_hyphen() -> None:
    r = parse_filename("Movie.1080p.Hindi-English.mkv")
    assert r.languages == ["English", "Hindi"]

def test_sep_underscore() -> None:
    r = parse_filename("Movie.1080p.Hindi_English.mkv")
    assert r.languages == ["English", "Hindi"]

def test_sep_plus() -> None:
    r = parse_filename("Movie.1080p.Hindi+English.mkv")
    assert r.languages == ["English", "Hindi"]

def test_sep_ampersand() -> None:
    r = parse_filename("Movie.1080p.Hindi&English.mkv")
    assert r.languages == ["English", "Hindi"]

def test_sep_tam_plus_eng() -> None:
    r = parse_filename("Movie.1080p.Tam+Eng.mkv")
    assert r.languages == ["English", "Tamil"]

def test_sep_tam_hyphen_eng() -> None:
    r = parse_filename("Movie.1080p.Tam-Eng.mkv")
    assert r.languages == ["English", "Tamil"]

def test_sep_tam_underscore_eng() -> None:
    r = parse_filename("Movie.1080p.Tam_Eng.mkv")
    assert r.languages == ["English", "Tamil"]

def test_sep_spaces_plus() -> None:
    r = parse_filename("Movie.1080p.Tam + Tel + Hin.mkv")
    assert r.languages == ["Hindi", "Tamil", "Telugu"]


# ══════════════════════════════════════════════════════════════════════════════
# 5. QUALITY FORMATS
# ══════════════════════════════════════════════════════════════════════════════

def test_quality_240p() -> None:
    assert parse_filename("M.240p.Hindi.mkv").quality == "240p"

def test_quality_360p() -> None:
    assert parse_filename("M.360p.Hindi.mkv").quality == "360p"

def test_quality_480p() -> None:
    assert parse_filename("M.480p.Hindi.mkv").quality == "480p"

def test_quality_576p() -> None:
    assert parse_filename("M.576p.Hindi.mkv").quality == "576p"

def test_quality_720p() -> None:
    assert parse_filename("M.720p.Hindi.mkv").quality == "720p"

def test_quality_1080p() -> None:
    assert parse_filename("M.1080p.Hindi.mkv").quality == "1080p"

def test_quality_1440p() -> None:
    assert parse_filename("M.1440p.Hindi.mkv").quality == "1440p"

def test_quality_2160p() -> None:
    assert parse_filename("M.2160p.Hindi.mkv").quality == "4K"

def test_quality_4k() -> None:
    assert parse_filename("M.4K.Hindi.mkv").quality == "4K"

def test_quality_uhd() -> None:
    assert parse_filename("M.UHD.Hindi.mkv").quality == "4K"

def test_quality_4320p() -> None:
    assert parse_filename("M.4320p.Hindi.mkv").quality == "8K"

def test_quality_8k() -> None:
    assert parse_filename("M.8K.Hindi.mkv").quality == "8K"


# ══════════════════════════════════════════════════════════════════════════════
# 6. DUAL AUDIO VARIANTS
# ══════════════════════════════════════════════════════════════════════════════

def test_dual_simple() -> None:
    assert parse_filename("M.1080p.Dual.mkv").languages == ["Dual Audio"]

def test_dual_audioword() -> None:
    assert parse_filename("M.1080p.DualAudio.mkv").languages == ["Dual Audio"]

def test_dual_audio_separate() -> None:
    assert parse_filename("M.1080p.Dual.Audio.mkv").languages == ["Dual Audio"]

def test_dual_audio_hyphen() -> None:
    assert parse_filename("M.1080p.Dual-Audio.mkv").languages == ["Dual Audio"]

def test_dual_uppercase() -> None:
    assert parse_filename("M.1080p.DUAL.mkv").languages == ["Dual Audio"]


# ══════════════════════════════════════════════════════════════════════════════
# 7. MULTI AUDIO VARIANTS
# ══════════════════════════════════════════════════════════════════════════════

def test_multi_simple() -> None:
    assert parse_filename("M.1080p.Multi.mkv").languages == ["Multi Audio"]

def test_multi_audioword() -> None:
    assert parse_filename("M.1080p.MultiAudio.mkv").languages == ["Multi Audio"]

def test_multi_audio_separate() -> None:
    assert parse_filename("M.1080p.Multi.Audio.mkv").languages == ["Multi Audio"]

def test_multi_audio_hyphen() -> None:
    assert parse_filename("M.1080p.Multi-Audio.mkv").languages == ["Multi Audio"]

def test_multi_uppercase() -> None:
    assert parse_filename("M.1080p.MULTI.mkv").languages == ["Multi Audio"]


# ══════════════════════════════════════════════════════════════════════════════
# 8. THREE+ LANGUAGES → MULTI AUDIO
# ══════════════════════════════════════════════════════════════════════════════

def test_three_langs_becomes_multi() -> None:
    r = parse_filename("Movie.1080p.Hin.Eng.Tam.mkv")
    assert r.languages == ["Hindi", "English", "Tamil"]
    assert "Multi Audio" in r.display_name

def test_five_langs_becomes_multi() -> None:
    r = parse_filename("Movie.1080p.Tam.Tel.Hin.Mal.Kan.mkv")
    assert r.languages == ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"]
    assert "Multi Audio" in r.display_name


# ══════════════════════════════════════════════════════════════════════════════
# 9. INVALID / MISSING FIELDS
# ══════════════════════════════════════════════════════════════════════════════

def test_missing_language() -> None:
    r = parse_filename("Movie.1080p.mkv")
    assert r.quality == "1080p"
    assert r.languages == []
    _assert_missing(r, quality=False, language=True)

def test_missing_quality() -> None:
    r = parse_filename("Movie.Hindi.mkv")
    assert r.quality is None
    assert r.languages == ["Hindi"]
    _assert_missing(r, quality=True, language=False)

def test_missing_both() -> None:
    r = parse_filename("Movie.mkv")
    assert r.quality is None
    assert r.languages == []
    _assert_missing(r, quality=True, language=True)

def test_missing_quality_movie_final_cut() -> None:
    r = parse_filename("Movie.Final.Cut.mkv")
    _assert_missing(r, quality=True, language=True)

def test_missing_quality_movie_new() -> None:
    r = parse_filename("Movie.NEW.mkv")
    _assert_missing(r, quality=True, language=True)

def test_empty_filename() -> None:
    r = parse_filename("")
    assert r.original_filename == ""
    assert r.display_name == ""


# ══════════════════════════════════════════════════════════════════════════════
# 10. WEIRD / EDGE CASE NAMES
# ══════════════════════════════════════════════════════════════════════════════

def test_weird_parentheses_quality() -> None:
    r = parse_filename("Movie (1080p) (Hindi).mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]

def test_weird_brackets() -> None:
    r = parse_filename("Movie_[1080p]_[Hindi].mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]

def test_weird_lowercase_quality() -> None:
    r = parse_filename("Movie 1080P HIN.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]

def test_weird_hyphen_case() -> None:
    r = parse_filename("Movie-1080P-HIN.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]

def test_weird_double_underscore() -> None:
    r = parse_filename("Movie__1080p__Hin.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]

def test_weird_triple_dot() -> None:
    r = parse_filename("Movie...1080p...Hin.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi"]


# ══════════════════════════════════════════════════════════════════════════════
# 11. SERIES / SEASON–EPISODE DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def test_se_sxxexx() -> None:
    r = parse_filename("Show.S03E05.720p.Tel.mkv")
    assert r.season == "03" and r.episode == "05"

def test_se_sxey_short() -> None:
    r = parse_filename("Show.S1E5.1080p.English.mkv")
    assert r.season == "01" and r.episode == "05"

def test_se_spelled_out() -> None:
    r = parse_filename("Show.Season 1 Episode 2.1080p.English.mkv")
    assert r.season == "01" and r.episode == "02"

def test_se_ep_format() -> None:
    r = parse_filename("Show.S01.EP.05.1080p.English.mkv")
    assert r.season == "01" and r.episode == "05"

def test_se_three_digit_episode() -> None:
    r = parse_filename("Arafta.S01E100.1080p.Hindi.mkv")
    assert r.season == "01" and r.episode == "100"

def test_se_ep_three_digit() -> None:
    r = parse_filename("Show.S01.EP.100.1080p.English.mkv")
    assert r.season == "01" and r.episode == "100"

def test_se_combined_hyphen() -> None:
    r = parse_filename("Show.S01.EP.21-24.1080p.Hindi.mkv")
    assert r.season == "01" and r.episode == "21" and r.episode_end == "24"

def test_se_combined_space_hyphen() -> None:
    r = parse_filename("Show.S01 EP 21-24.1080p.Hindi.mkv")
    assert r.season == "01" and r.episode == "21" and r.episode_end == "24"

def test_se_no_season_only_title() -> None:
    r = parse_filename("Movie.1080p.Hindi.mkv")
    assert r.season is None and r.episode is None


# ══════════════════════════════════════════════════════════════════════════════
# 12. REAL COLLECTION — Theatre Movies
# ══════════════════════════════════════════════════════════════════════════════

def test_real_supergirl_hindi_english() -> None:
    r = parse_filename("SuperGirl.2026.1080p.V2-HDTC.Hindi-English.LiNE.x264")
    assert r.quality == "1080p"
    assert r.languages == ["English", "Hindi"]

def test_real_con_city_250mb() -> None:
    r = parse_filename("Con City 2026 Tamil HQ PreDVD - x264 - HQ Clean - AAC - 250MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_con_city_700mb() -> None:
    r = parse_filename("Con City 2026 Tamil HQ PreDVD - x264 - HQ Clean - AAC - 700MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_con_city_720p_1_4gb() -> None:
    r = parse_filename("Con City 2026 Tamil HQ PreDVD - 720p - x264 - HQ Clean - AAC - 1.4GB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["Tamil"]

def test_real_con_city_720p_900mb() -> None:
    r = parse_filename("Con City 2026 Tamil HQ PreDVD - 720p - x264 - HQ Clean - AAC - 900MB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["Tamil"]

def test_real_con_city_1080p() -> None:
    r = parse_filename("Con City 2026 Tamil HQ PreDVD - 1080p - x264 - HQ Clean - AAC - 2.7GB.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Tamil"]

def test_real_angikaaram_400mb() -> None:
    r = parse_filename("Angikaaram 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 400MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_angikaaram_250mb() -> None:
    r = parse_filename("Angikaaram 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 250MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_angikaaram_700mb() -> None:
    r = parse_filename("Angikaaram 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 700MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_angikaaram_720p() -> None:
    r = parse_filename("Angikaaram 2026 Tamil PreDVD - 720p - x264 - HQ Clean - AAC - 1.4GB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["Tamil"]

def test_real_angikaaram_1080p() -> None:
    r = parse_filename("Angikaaram 2026 Tamil PreDVD - 1080p - x264 - HQ Clean - AAC - 2.5GB.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Tamil"]

def test_real_supergirl_tamil_400mb() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - x264 - Tamil Dub - HQ Clean - AAC - 400MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_supergirl_tamil_eng_720p() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - 720p - x264 - Tam + Eng - HQ Clean - AAC - 1GB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["English", "Tamil"]

def test_real_supergirl_tamil_eng_1080p() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - 1080p - x264 - Tam + Eng - HQ Clean - AAC - 2GB.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["English", "Tamil"]

def test_real_supergirl_telugu_400mb() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - x264 - Tel Dub - HQ Clean - AAC - 400MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Telugu"]

def test_real_supergirl_telugu_eng_720p() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - 720p - x264 - Tel + Eng - HQ Clean - AAC - 1GB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["English", "Telugu"]

def test_real_supergirl_telugu_eng_1080p() -> None:
    r = parse_filename("Supergirl 2026 HQ PreDVD - 1080p - x264 - Tel + Eng - HQ Clean - AAC - 2GB.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["English", "Telugu"]

def test_real_heartin_250mb() -> None:
    r = parse_filename("Heartin 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 250MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_heartin_400mb() -> None:
    r = parse_filename("Heartin 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 400MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_heartin_700mb() -> None:
    r = parse_filename("Heartin 2026 Tamil PreDVD - x264 - HQ Clean - AAC - 700MB.mkv")
    _assert_missing(r, quality=True, language=False)
    assert r.languages == ["Tamil"]

def test_real_heartin_1080p() -> None:
    r = parse_filename("Heartin 2026 Tamil PreDVD - 1080p - x264 - HQ Clean - AAC - 2.2GB.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Tamil"]

def test_real_heartin_720p() -> None:
    r = parse_filename("Heartin 2026 Tamil PreDVD - 720p - x264 - HQ Clean - AAC - 1.2GB.mkv")
    assert r.quality == "720p"
    assert r.languages == ["Tamil"]


# ══════════════════════════════════════════════════════════════════════════════
# 13. REAL COLLECTION — Series Channel (Arafta)
# ══════════════════════════════════════════════════════════════════════════════

def test_real_rafta_e73() -> None:
    r = parse_filename("Arafta.S01E73.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    _assert_missing(r, quality=False, language=True)
    assert r.season == "01" and r.episode == "73"

def test_real_rafta_e74() -> None:
    r = parse_filename("Arafta.S01E74.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    _assert_missing(r, quality=False, language=True)
    assert r.season == "01" and r.episode == "74"

def test_real_rafta_e100() -> None:
    r = parse_filename("Arafta.S01E100.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    assert r.season == "01" and r.episode == "100"

def test_real_rafta_e87() -> None:
    r = parse_filename("Arafta.S01E87.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    assert r.season == "01" and r.episode == "87"

def test_real_rafta_e92() -> None:
    r = parse_filename("Arafta.S01E92.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    assert r.season == "01" and r.episode == "92"

def test_real_rafta_e99() -> None:
    r = parse_filename("Arafta.S01E99.1080p.AMZN.WEB-DL.DDP2.0.H.265-XDMOViES.mkv")
    assert r.quality == "1080p"
    assert r.season == "01" and r.episode == "99"


# ══════════════════════════════════════════════════════════════════════════════
# 14. REAL COLLECTION — Brothers & Sisters (single episodes)
# ══════════════════════════════════════════════════════════════════════════════

def test_real_brothers_single_e21_no_meta() -> None:
    r = parse_filename("Brothers and Sisters S01E21 Harini Says No.mkv")
    _assert_missing(r, quality=True, language=True)
    assert r.season == "01" and r.episode == "21"

def test_real_brothers_single_e22_no_meta() -> None:
    r = parse_filename("Brothers and Sisters S01E22 Jaggu Learns About Madhus Family.mkv")
    _assert_missing(r, quality=True, language=True)
    assert r.season == "01" and r.episode == "22"

def test_real_brothers_single_e23_no_meta() -> None:
    r = parse_filename("Brothers and Sisters S01E23 The Children Plot Against SS.mkv")
    _assert_missing(r, quality=True, language=True)
    assert r.season == "01" and r.episode == "23"

def test_real_brothers_single_e24_no_meta() -> None:
    r = parse_filename("Brothers and Sisters S01E24 Jayshree Tells the Truth.mkv")
    _assert_missing(r, quality=True, language=True)
    assert r.season == "01" and r.episode == "24"


# ══════════════════════════════════════════════════════════════════════════════
# 15. REAL COLLECTION — Brothers & Sisters (combined + multi audio)
# ══════════════════════════════════════════════════════════════════════════════

def test_real_brothers_combined_720p() -> None:
    r = parse_filename("Brothers And Sisters 2026 S01 EP 21-24 COMBiNED TRUE WEB-DL - 720p - AVC - Tam + Tel + Hin + Mal + Kan - AAC - 1.2GB - ESub.mkv")
    assert r.quality == "720p"
    assert r.languages == ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"]
    assert r.season == "01" and r.episode == "21" and r.episode_end == "24"
    assert "Multi Audio" in r.display_name

def test_real_brothers_combined_480p() -> None:
    r = parse_filename("Brothers And Sisters 2026 S01 EP 21-24 COMBiNED TRUE WEB-DL - 480p - AVC - Tam + Tel + Mal - AAC - 550MB - ESub.mkv")
    assert r.quality == "480p"
    assert r.languages == ["Tamil", "Telugu", "Malayalam"]
    assert r.season == "01" and r.episode == "21" and r.episode_end == "24"

def test_real_brothers_combined_1080p() -> None:
    r = parse_filename("Brothers And Sisters 2026 S01 EP 21-24 COMBiNED TRUE WEB-DL - 1080p - AVC - Tam + Tel + Hin + Mal + Kan - AAC - 3.4GB - ESub.mkv")
    assert r.quality == "1080p"
    assert r.languages == ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"]
    assert r.season == "01" and r.episode == "21" and r.episode_end == "24"

def test_real_brothers_e21_480p() -> None:
    r = parse_filename("Brothers and Sisters S01E21 Harini Says No.480p.Tam.Tel.Hin.mkv")
    assert r.quality == "480p"
    assert r.languages == ["Hindi", "Tamil", "Telugu"]
    assert r.season == "01" and r.episode == "21"


# ══════════════════════════════════════════════════════════════════════════════
# 16. DISPLAY NAME / MISC PROPERTIES
# ══════════════════════════════════════════════════════════════════════════════

def test_preserves_original_filename() -> None:
    r = parse_filename("My.Movie.2023.1080p.Hindi.mkv")
    assert r.original_filename == "My.Movie.2023.1080p.Hindi.mkv"
    assert r.display_name != r.original_filename

def test_parsed_file_default_fields() -> None:
    r = parse_filename("Test.1080p.English.mkv")
    assert r.file_id is None
    assert r.file_unique_id is None
    assert r.file_size == 0
    assert r.mime_type is None
    assert r.season is None
    assert r.episode is None
    assert r.episode_end is None
    assert r.use_original_filename is False

def test_display_name_hindi_plus_english() -> None:
    r = parse_filename("Test.1080p.Hin.Eng.mkv")
    assert "Hindi + English" in r.display_name

def test_display_name_dual_audio() -> None:
    r = parse_filename("Test.4K.Dual.Audio.mkv")
    assert "Dual Audio" in r.display_name
    assert "4K" in r.display_name

def test_display_name_multi_audio() -> None:
    r = parse_filename("Test.720p.Multi.mkv")
    assert "Multi Audio" in r.display_name

def test_display_name_three_languages() -> None:
    r = parse_filename("Test.1080p.Hin.Eng.Tam.mkv")
    assert "Multi Audio" in r.display_name

def test_display_name_missing_quality_shows_shrug() -> None:
    r = parse_filename("Test.Hindi.mkv")
    assert "\U0001F937" in r.display_name

def test_display_name_missing_language_shows_shrug() -> None:
    r = parse_filename("Test.1080p.mkv")
    assert "\U0001F937" in r.display_name

def test_display_name_season_episode() -> None:
    r = parse_filename("Show.S01E05.1080p.English.mkv")
    assert "S01E05" in r.display_name

def test_display_name_combined_episode() -> None:
    r = parse_filename("Show.S01.EP.21-24.1080p.Hindi.mkv")
    assert "S01" in r.display_name
    assert "EP21" in r.display_name
    assert "\u201324" in r.display_name
