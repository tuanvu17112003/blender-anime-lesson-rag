"""Fetch playlist inventories, YouTube transcripts/metadata, free web guides, and companion GitHub repos
for the 3D Anime Character Modeling, Rigging, Shading & Animation RAG knowledge base.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw_sources"
YT_DIR = RAW / "youtube"
YT_VIDEOS_DIR = YT_DIR / "videos"
WEB_DIR = RAW / "web"
GH_DIR = RAW / "github"

PLAYLISTS = {
    "daniel_kreuter_2022_blender3": "https://www.youtube.com/playlist?list=PLvgIVNDU-Dxi5h3JLNJMfK0t3-WsBm6Av",
    "daniel_kreuter_2020_anime": "https://www.youtube.com/playlist?list=PLvgIVNDU-Dxge794BXoeQsDxb9u_3TZas",
    "daniel_kreuter_2014_anime_2": "https://www.youtube.com/playlist?list=PLvgIVNDU-Dxjb3eukDF5W0l0-6ShO9OiM",
    "daniel_kreuter_rigging_guide": "https://www.youtube.com/playlist?list=PLvgIVNDU-Dxhk8lbxDHGid_Im7iioBXna",
    "crashsune_full_character_2024": "https://www.youtube.com/playlist?list=PLcaQc6eQjXCxWXmn5jxE_GTOft9ZxChu1",
    "crashsune_lowpoly_anime": "https://www.youtube.com/playlist?list=PLcaQc6eQjXCzYski4EEr-iRfdkXkX-P3g",
    "crashsune_anime_shaders": "https://www.youtube.com/playlist?list=PLcaQc6eQjXCyJXPC6DItWCrMAvjrpbcWk",
    "crashsune_animation_full": "https://www.youtube.com/playlist?list=PLcaQc6eQjXCxFhrsFWWemTkxAWwAmbxzi",
    "crashsune_blender_vrchat": "https://www.youtube.com/playlist?list=PLcaQc6eQjXCwY-bi_WzxCK5BuFeiQuUFA",
    "dikko_modeling_for_animation": "https://www.youtube.com/playlist?list=PLL3OEv6vd5VA4owAPOI0QdCcEmvl1f3BT",
    "dikko_rigging_characters": "https://www.youtube.com/playlist?list=PLL3OEv6vd5VA8_FBkeitaeqC0kbcrhMTC",
    "dikko_texturing_stylised": "https://www.youtube.com/playlist?list=PLL3OEv6vd5VCoUPgYfR_DoCKBtzMmXc11",
    "dikko_animation": "https://www.youtube.com/playlist?list=PLL3OEv6vd5VAsVqOFCTfPzc1rSgkZvcTm",
    "cgdive_weight_paint": "https://www.youtube.com/playlist?list=PLdcL5aF8ZcJsFEdlMJ7To0Iu9s-XCFV3W",
    "cgdive_rigify_advanced": "https://www.youtube.com/playlist?list=PLdcL5aF8ZcJttvb-rgvyA1NkRi77zVP-J",
    "cgdive_blender_to_unity": "https://www.youtube.com/playlist?list=PLdcL5aF8ZcJtDzChFfO9smj6M_EDoJ2uM",
    "cgdive_jiggles_muscles": "https://www.youtube.com/playlist?list=PLdcL5aF8ZcJuJcy5-mLylDQrMxbvQuaKE",
    "royal_skies_anime_shading": "https://www.youtube.com/playlist?list=PLZpDYt0cyiusDdsgdb9FgfT7onV7th8mJ",
    "royal_skies_rigging_crash": "https://www.youtube.com/playlist?list=PLZpDYt0cyiuvuzHga3apBwSaCD7MTrv8L",
    "royal_skies_speed_rigging": "https://www.youtube.com/playlist?list=PLZpDYt0cyiusytIPAOTPRzsa4GK6LgY3_",
    "lightning_boy_toon_shader": "https://www.youtube.com/playlist?list=PLZ7TSA6MfgM_IX3qZslXx_QdvLLDZHZGx",
    "joey_carlino_modeling_sculpting": "https://www.youtube.com/playlist?list=PLzg4_2BrWAVyf8LKdr2XtEw2BCDvbEnuk",
    "joey_carlino_rigging": "https://www.youtube.com/playlist?list=PLzg4_2BrWAVwkQvVPJoNaXNN4dXY0Xjkl",
}

GITHUB_REPOS = {
    "VRM_Addon_for_Blender": "https://github.com/saturday06/VRM-Addon-for-Blender.git",
    "GabrielToonShader": "https://github.com/gabriel01913/GabrielToonShader.git",
    "Blender_Wiggle_2": "https://github.com/shteeve3d/blender-wiggle-2.git",
    "BNPR_Abnormal": "https://github.com/bnpr/Abnormal.git",
    "VRM_Specification": "https://github.com/vrm-c/vrm-specification.git",
}

# Curated high-signal YouTube videos covering all 3D Anime pipeline stages
CURATED_VIDEO_IDS: list[tuple[str, str]] = [
    # Full Courses / End-to-End Anime Character Pipelines
    ("EQHdi5rX5fs", "crashsune_lowpoly_anime_full_4h"),
    ("xZWxEoa-Dwk", "noggi_everything_beautiful_3d_anime"),
    ("4LhvcINgNxU", "sunny_dillongoo_make_anime_3d"),
    ("w064sEhntpc", "shonzo_modeling_3d_anime_face_czn"),
    ("HHCGrbeTWww", "shonzo_new_anime_style_modeling_guide"),
    ("Sy7RHtco43Y", "natsumori_katsu_modeling_rigify_unity_vrchat"),
    ("4KOoN65ZcrI", "asw_guilty_gear_anime_modeling_tips"),
    ("yhGjCzxJV3E", "asw_guilty_gear_xrd_gdc_art_style"),
    ("yg8Snn3OzLc", "chaosy3d_create_anime_girl_body"),
    ("fNxdOtegry0", "silverwilliam_modeling_anime_head"),
    # Daniel Kreuter Masterclasses
    ("Kna9OVFO5cc", "kreuter_2022_01_blender3_intro"),
    ("0k8yFiTE0PU", "kreuter_2022_03_base_mesh_1"),
    ("m07lmeqzwPE", "kreuter_2022_12_high_poly_4"),
    ("Rj0hn9qGztM", "kreuter_2020_02_sculpting_intro"),
    ("AlX-wVx-NNU", "kreuter_24p_01_reference_eyes"),
    ("RtrOSuAGFgQ", "kreuter_24p_02_nose"),
    ("1oAicxULj20", "kreuter_24p_06_head"),
    ("THy75CdMrNM", "kreuter_24p_10_upper_body"),
    ("JW7ffsHWv4s", "kreuter_24p_24_detail"),
    ("F1CTfis1TEg", "kreuter_40p_01_reference_basemesh"),
    # 2AM Anime Character Series
    ("NCIOXxjw8BQ", "2am_01_anime_girl_from_scratch"),
    ("uptuXWNWpk0", "2am_anime_face_explained_custom_shadows"),
    ("hZMO3OgV-Lw", "2am_3d_anime_eyes_like_pro"),
    ("3guG5h5jX-E", "2am_beautiful_3d_hair_like_pro"),
    ("LU0BFThJIco", "2am_hair_full_workflow_model_texture_normals"),
    ("oKfFi1MpO9c", "2am_clean_anime_shading_edit_normals_1min"),
    ("x-K6bCAl6Qs", "2am_perfect_anime_face_shadows"),
    ("blgGcbZzsWM", "2am_rig_everything_hair_chest_clothes"),
    ("Qyrz4JoMP28", "2am_blinking_lipsync_export"),
    ("9hNmJYqKQys", "2am_reverse_engineer_3d_art_style"),
    # Face Topology, Sculpting & Retopology
    ("J2_uiUEcY7w", "bran_sculpts_blocking_out_character"),
    ("0SRq5i_v83c", "bran_sculpts_ryuko_anime"),
    ("F_RgaCzgMwQ", "flycat_anime_character_sculpt_4_3"),
    ("FkWvgT75SbA", "flycat_sculpting_retopology_p1"),
    ("QVwzmYTNMZc", "maoly_face_modeling_without_sculpting"),
    ("rvDf6ZuEynM", "maoly_face_retopology_no_addon"),
    ("5DaLb-d5Ies", "maoly_sculpt_stylized_face"),
    ("0aPr51sDkxE", "vertex_arcade_retopologize_stylized"),
    ("X2GNyEUvpD4", "cgboost_retopology_beginner"),
    ("3EG7krYP1h0", "anton_correct_character_retopology"),
    ("ilzlcTb4GTk", "kenny_praise_ultimate_retopology_guide"),
    ("O6HQhs-gk50", "joey_carlino_character_modeling_beginners"),
    ("01WQlMD7dsk", "dikko_modeling_for_animation_01_top5"),
    ("QboreU0cRjY", "dikko_character_modeling_02_blockout"),
    ("GxMz4HylQfU", "dikko_modeling_for_animation_03_volume"),
    ("8R0e0qh5wiU", "dikko_modeling_for_animation_04_hands"),
    ("SwM19PgSdCM", "dikko_modeling_for_animation_06_face_retopo"),
    ("wXem71To_KA", "crashsune_04_model_face"),
    ("GAoaBfMqSBo", "crashsune_model_rig_lowpoly_eyes_4_4"),
    ("fxnfX3rIFbY", "crashsune_03_upper_body"),
    # Anime Hair, Clothes & Texturing
    ("Ng8FbOHvsLQ", "natsumori_katsu_hair_modeling_curves"),
    ("BqWYgrXw7Jk", "yansculpts_easiest_hair_5min"),
    ("ethg2nYSjqg", "itspaultodd_fast_stylized_hair_4_0"),
    ("HGKYUWI44lQ", "astonished_gacha_anime_hair_ucupaint"),
    ("46F7k4fvsN8", "riel_stylized_hair_hairmesh_guide"),
    ("jYgiT35wES0", "chicha_subculture_anime_hair_vtuber"),
    ("Qk6nGcURdpY", "messymesh_anime_hair_beginner"),
    ("SFdLEc2G_Jk", "crashsune_lowpoly_hair_texture"),
    ("pKOlyzXFf4U", "crashsune_07_uv_unwrapping_texturing"),
    ("gOvm7XuI9Qo", "pyrodev_handpainting_anime_texture"),
    ("ATClZK6W5a8", "facepalme_texture_anime_head"),
    ("aKpIM5DZaFc", "maoly_paint_character_2_methods"),
    # Cel Shading, Face Normals & Outlines
    ("0k-xHSvLVi8", "facepalme_advanced_anime_face_shading"),
    ("KB0B9Hz46UM", "animexd_mastering_editing_normals"),
    ("1puHJSkZy24", "animexd_editing_normals_anime_shading"),
    ("79XKQVAS9dI", "3dcinetv_normal_editing_anime_faces_101"),
    ("aIA7tkd-M5o", "3dcinetv_guilty_gear_shader_p4"),
    ("9JiewKzta7Y", "fondant_clean_normals_toon_addon"),
    ("PX_yRZOdb7M", "cofeemug_top3_anime_outline_eevee"),
    ("tWcaQ3gCbUU", "guilty_gear_3d_look_2d_study"),
    ("dybTdt9WXts", "blender_secrets_inverted_hull_5_2"),
    ("QGV3v0wom1E", "blender_secrets_inverted_hull_cycles"),
    ("J5YfZwzARNo", "royalskies_anime_shading_intro"),
    ("XEn1bXeG9bo", "royalskies_smoothing_normals_easy"),
    ("n-FJb7QW0Ww", "royalskies_complete_anime_shading_2min"),
    ("zI3FoxDpH-k", "royalskies_material_based_anime_shading"),
    ("1n0BL4iDZJk", "royalskies_anime_color_mapping"),
    ("8-42DOMuWok", "royalskies_anime_shader_detail_color_maps"),
    ("iHy5GjQmxTc", "royalskies_anime_hair_shader_2min"),
    ("otefqCPhPHM", "royalskies_anime_tutorial_conclusion"),
    ("TpWI2rU8iF0", "lightningboy_toon_p1_multi_lights"),
    ("hp4V-9oFmnM", "lightningboy_toon_p2_dynamic_outlines"),
    ("kxWWBmIUxbc", "lightningboy_toon_p4_anisotropic_hair"),
    ("ToX21Z8RXoc", "lightningboy_toon_p5_better_shadows"),
    ("Qc1kQbF-9Gs", "lightningboy_toon_p6_rim_lights"),
    ("C4jkUtfbbbE", "lightningboy_toon_face_rig_booleans"),
    # Rigging, Weight Painting, Skirts/Clothes & Facial Shape Keys
    ("4O3OKhYxNx8", "crashsune_09_rig_rigify_8min"),
    ("IOjH0eG43Ak", "tomcat_rigify_long_hair_body_face"),
    ("m-Obo_nC3SM", "joey_carlino_rigging_for_beginners"),
    ("kkX50pkZT1s", "dikko_rigging_01_top10_best_practices"),
    ("vbF78A50D0w", "dikko_rigging_02a_four_components"),
    ("j_Buujl3HvI", "dikko_rigging_05_arm_rig"),
    ("yYZhJw_WVm8", "dikko_rigging_08_hands"),
    ("-HpDSAwcp8s", "dikko_rigging_09_head_jaw"),
    ("K5nMXJg55_k", "dikko_rigging_10_face_shape_keys"),
    ("eoird3MVCNw", "cgdive_rigify_4_0_ch2_basics"),
    ("7D8HtiSrDCk", "cgdive_4_0_whats_new_rigify"),
    ("tNW8uCs77MQ", "cgdive_solid_weight_painting_workflow"),
    ("Jtse_jUq7rk", "cgdive_4_0_rigging_animation_features"),
    ("mv2_WYH6OV0", "cgdive_4_3_4_4_rigging_animation_features"),
    ("dF2OQwpDHQk", "cgdive_rigify_deform_bones"),
    ("4VI5jk7pZag", "pierrick_trick_weight_painting_easy"),
    ("tRgh8doVYzI", "pierrick_secret_weight_painting_skinning"),
    ("wDujpiW4q_A", "pierrick_rigging_automatic_weights"),
    ("55bJB5Wmd_U", "pierrick_skirt_dress_rigging"),
    ("kCn4sProaek", "pierrick_dynamic_cloth_rigging"),
    ("Xy6DHSEl5Cs", "pierrick_tails_whip_chains_rigging"),
    ("cGcBfhYyjC8", "kanafuyuko_rig_dresses_skirts_physics"),
    ("k8DQY_DNDPM", "chiimera_weight_paint_vrchat"),
    ("tUIIauuXveE", "ozzo_weight_painting_beginner_to_pro"),
    ("kssTxoyd_C8", "sorrystacy_rigging_weight_painting"),
    ("6s-CXmHMAVs", "mojogamedev_attach_clothes_2min"),
    ("s4-4CSTMoe0", "oby1_rig_clothes_easy_way"),
    ("X590IZeyT1s", "royalskies_rig_character_5min"),
    ("gTdRGZA4TXA", "royalskies_hair_rigging_physics_2min"),
    ("bqjM49G_MDY", "royalskies_facial_shapekeys_fast"),
    ("1Is3oUvHwdM", "vertex_arcade_4_0_facial_anim_no_rigging"),
    ("qlvrwK4htWk", "shonzo_face_expressions_shape_keys"),
    ("yg3RSTV2JnQ", "pixxo3d_facial_shapekeys_beginners"),
    ("SRkgfEM7oYw", "nukorio_lazy_mouth_rig"),
    ("haPsP5EfVTY", "freedom_arts_blender_5_0_fbx_shapekeys"),
    # Anime Animation, Stepped 2s, Smears, Cycles & Actions
    ("wwJpW-OANR8", "dillongoo_bloop_run_cycle"),
    ("QqBxR1QuemQ", "pierrick_principles_of_animation_blender"),
    ("5QAdQwCRbBM", "pierrick_animation_tool_always_use"),
    ("KNZ0x1bXwNs", "pierrick_8_tips_improve_animation"),
    ("SLh3hUIxv1s", "pierrick_walk_cycle_blender"),
    ("bNNL0tW0oh8", "dikko_fix_bad_walk_cycles"),
    ("LCl2cTMaW7E", "crashsune_lowpoly_animations_blender"),
    ("1l1LBCtyh-8", "royalskies_idle_animation_60s"),
    ("qxoo_bcUZos", "royalskies_animate_running_2min"),
    ("06_puGmTIko", "royalskies_complex_motions_2min"),
    ("OhI4zD7-qmE", "royalskies_directional_strafing_2min"),
    ("1HXOlu0awmI", "royalskies_flips_spins_problems"),
    ("L4OcpF7-YB0", "royalskies_import_rigs_anim_unreal"),
    ("hfUbh6igfpA", "pressup_choppy_animation_blender"),
    ("dEhR6q7Z8Pk", "pressup_choppy_animation_tutorial"),
    ("BBoVomEOKbc", "doodley_why_choppy_animation_better"),
    ("6lGPvMLE8Oo", "doodley_animating_legs_walk_weight"),
    ("ArrJe4c9ar8", "christopher3d_blender_4_4_action_slots"),
    ("HCdynE4IL5c", "southernshotty_blender_4_4_action_slots"),
    ("Y4nVQTZSWao", "southernshotty_new_animation_feature"),
    ("TgOllr05aCs", "3dan_smear_frames_4_5"),
    ("v6hwWuZeWig", "joeycquel_auto_smear_frames"),
    ("K1g2fSuVFs0", "ashlee3dee_toon_anime_smears_geonodes"),
]


def clean_vtt(vtt_text: str) -> str:
    """Parse VTT captions into deduplicated readable lines."""
    lines: list[str] = []
    seen_recent: list[str] = []
    tag_re = re.compile(r"<[^>]+>")
    ts_re = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->")
    for raw in vtt_text.splitlines():
        s = raw.strip()
        if not s or s == "WEBVTT" or s.startswith(("Kind:", "Language:", "NOTE")) or ts_re.match(s):
            continue
        if s.isdigit():
            continue
        s = tag_re.sub("", s)
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue
        if s in seen_recent[-4:]:
            continue
        seen_recent.append(s)
        lines.append(s)
    return "\n".join(lines)


def inspect_playlists() -> dict:
    YT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for key, url in PLAYLISTS.items():
        if not url.startswith("https://"):
            raise ValueError(f"Refusing non-HTTPS playlist URL for {key}")
        proc = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-single-json", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
        )
        if proc.returncode != 0:
            print(f"[ERR] {key}: {proc.stderr[:200]}", file=sys.stderr)
            continue
        data = json.loads(proc.stdout)
        entries = [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "duration": e.get("duration"),
                "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
            }
            for e in (data.get("entries") or [])
            if e.get("id")
        ]
        summary[key] = {
            "playlist_title": data.get("title"),
            "uploader": data.get("uploader") or data.get("channel"),
            "url": url,
            "count": len(entries),
            "entries": entries,
        }
        print(f"{key}: {len(entries)} videos ({data.get('title')})", flush=True)
    out = YT_DIR / "playlists_index.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


JP_VIDEOS = {"Ng8FbOHvsLQ", "Sy7RHtco43Y", "4KOoN65ZcrI"}


def fetch_one_video(vid: str, alias: str) -> tuple[str, str]:
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,24}", vid):
        raise ValueError(f"Invalid YouTube video id: {vid!r}")
    safe_alias = re.sub(r"[^A-Za-z0-9_.-]+", "_", alias).strip("._") or vid
    YT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = (YT_VIDEOS_DIR / f"{safe_alias}__{vid}.json").resolve()
    if not meta_path.is_relative_to(YT_VIDEOS_DIR.resolve()):
        raise ValueError(f"Unsafe target path rejected: {meta_path}")
    if meta_path.exists():
        return safe_alias, "cached"
    # Clean stale temp files if any
    for stale in YT_VIDEOS_DIR.glob(f"_tmp_{vid}*"):
        stale.unlink(missing_ok=True)

    url = f"https://www.youtube.com/watch?v={vid}"
    tmp_prefix = YT_VIDEOS_DIR / f"_tmp_{vid}"
    sub_langs = "en-US,en,ja" if vid in JP_VIDEOS else "en,en-US,en-GB"

    def run_ytdlp(write_subs: bool, write_auto: bool) -> subprocess.CompletedProcess | None:
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-info-json",
            "--ignore-errors",
            "--no-abort-on-error",
            "--sleep-requests",
            "1.5",
            "--retries",
            "2",
            "--js-runtimes",
            "node",
            "-o",
            str(tmp_prefix),
            url,
        ]
        if write_subs:
            cmd.extend(["--write-subs", "--sub-langs", sub_langs, "--sub-format", "vtt"])
        if write_auto:
            cmd.extend(["--write-auto-subs", "--sub-langs", sub_langs, "--sub-format", "vtt"])
        try:
            return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
        except subprocess.TimeoutExpired:
            return None

    info_file = YT_VIDEOS_DIR / f"_tmp_{vid}.info.json"
    # Try 1: manual + auto subs (only single-language family to avoid 429s)
    proc = run_ytdlp(write_subs=True, write_auto=True)
    if not info_file.exists():
        time.sleep(3)
        # Fallback 2: manual subs only (no auto-sub rate limit)
        proc = run_ytdlp(write_subs=True, write_auto=False)
    if not info_file.exists():
        time.sleep(2)
        # Fallback 3: metadata + chapters only
        proc = run_ytdlp(write_subs=False, write_auto=False)

    if not info_file.exists():
        err_lines = [ln for ln in ((proc.stderr if proc else "") or "").splitlines() if "ERROR:" in ln or "429" in ln]
        tail = " | ".join(err_lines)[:180] if err_lines else ((proc.stderr if proc else "timeout") or "")[-180:]
        return alias, f"err:{proc.returncode if proc else -1}:{tail}"

    info = json.loads(info_file.read_text(encoding="utf-8", errors="replace"))
    vtt_files = sorted(YT_VIDEOS_DIR.glob(f"_tmp_{vid}*.vtt"))
    chosen_vtt = None
    for vf in vtt_files:
        if ".en" in vf.name:
            chosen_vtt = vf
            break
    if chosen_vtt is None and vtt_files:
        chosen_vtt = vtt_files[0]

    transcript = ""
    sub_lang = ""
    if chosen_vtt is not None:
        sub_lang = chosen_vtt.stem.split(".")[-1]
        transcript = clean_vtt(chosen_vtt.read_text(encoding="utf-8", errors="replace"))
    for vf in vtt_files:
        vf.unlink(missing_ok=True)
    info_file.unlink(missing_ok=True)

    record = {
        "id": vid,
        "alias": alias,
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "webpage_url": info.get("webpage_url") or url,
        "description": info.get("description") or "",
        "chapters": info.get("chapters") or [],
        "tags": (info.get("tags") or [])[:20],
        "sub_lang": sub_lang,
        "transcript": transcript,
    }
    meta_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return alias, f"ok(lang={sub_lang or 'none'},chapters={len(record['chapters'])},chars={len(transcript)})"


def fetch_videos(include_playlists: bool = True) -> None:
    targets: dict[str, str] = {vid: alias for vid, alias in CURATED_VIDEO_IDS}
    if include_playlists:
        idx_path = YT_DIR / "playlists_index.json"
        if idx_path.exists():
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            for pl_key in (
                "crashsune_full_character_2024",
                "crashsune_lowpoly_anime",
                "crashsune_anime_shaders",
                "royal_skies_anime_shading",
                "dikko_modeling_for_animation",
                "dikko_rigging_characters",
            ):
                pl = idx.get(pl_key, {})
                for i, e in enumerate(pl.get("entries", []), 1):
                    vid = e["id"]
                    if vid and vid not in targets:
                        targets[vid] = f"{pl_key}_{i:02d}"
    print(f"Fetching {len(targets)} YouTube videos...", flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futs = [pool.submit(fetch_one_video, vid, alias) for vid, alias in targets.items()]
        for fut in as_completed(futs):
            alias, status = fut.result()
            print(f"  [{status}] {alias}", flush=True)


def clone_github_repos() -> None:
    GH_DIR.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    for name, url in GITHUB_REPOS.items():
        if not url.startswith("https://"):
            raise ValueError(f"Refusing non-HTTPS repository URL for {name}")
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
        dest = (GH_DIR / safe_name).resolve()
        if not dest.is_relative_to(GH_DIR.resolve()):
            raise ValueError(f"Unsafe repo destination rejected: {dest}")
        if dest.exists():
            print(f"  [cached] {name}", flush=True)
            continue
        print(f"  [cloning] {name}...", flush=True)
        try:
            proc = subprocess.run(
                ["git", "clone", "--depth", "1", "--single-branch", url, str(dest)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=90,
            )
            if proc.returncode == 0:
                py_count = sum(1 for _ in dest.rglob("*.py"))
                md_count = sum(1 for _ in dest.rglob("*.md"))
                print(f"  [cloned] {name}: {py_count} .py, {md_count} .md", flush=True)
            else:
                print(f"  [err] {name}: {proc.stderr.strip()[:160]}", flush=True)
        except subprocess.TimeoutExpired:
            print(f"  [timeout] {name}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("playlists", "all"):
        inspect_playlists()
    if cmd in ("github", "all"):
        clone_github_repos()
    if cmd in ("videos", "all"):
        fetch_videos()
