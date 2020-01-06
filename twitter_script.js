function add_twitter_link() {
    var blog_url = encodeURIComponent(document.location);
    var blog_title = encodeURIComponent(document.title);
    var url = "https://twitter.com/intent/tweet?text=" + blog_title + "&url=" + blog_url + "&via=Bystroushaak";

    var twitter_link = document.getElementById("twitter_button");
    twitter_link.href = url;
    twitter_link.style.visibility = "visible";
}
