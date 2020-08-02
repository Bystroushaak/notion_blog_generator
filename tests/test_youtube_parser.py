from lib.html_transformers.fix_youtube_embeds import FixYoutubeEmbeds


def test_long_url_parse():
    url = "https://www.youtube.com/watch?feature=player_detailpage&amp;v=GIw7dJg1L84#t=4932"

    assert FixYoutubeEmbeds._parse_yt_embed_url(url) == "GIw7dJg1L84?start=4932"
