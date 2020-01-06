function add_twitter_link() {
    twitter_link = document.getElementById("twitter_button");
    blog_url = encodeURIComponent(document.location);
    blog_title = encodeURIComponent(document.title);
    url = "https://twitter.com/intent/tweet?text=" + blog_title + "&url=" + blog_url + "&via=Bystroushaak";
    twitter_link.href = url;
}
