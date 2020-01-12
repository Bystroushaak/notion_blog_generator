function add_twitter_link() {
    var blog_url = encodeURIComponent(document.location);
    var blog_title = encodeURIComponent(document.title);
    var url = "https://twitter.com/intent/tweet?text=" + blog_title + "&url=" + blog_url + "&via=Bystroushaak";

    var twitter_link = document.getElementById("twitter_button");
    twitter_link.href = url;
    twitter_link.style.visibility = "visible";
}

function add_image_overlays() {
    var figures = document.getElementsByTagName("figure");
    var figures_list = Array.prototype.slice.call(figures);

    figures_list.forEach(function (figure){
        var imgs = figure.getElementsByTagName("img");

        if (imgs.length === 0)
            return;

        var links = figure.getElementsByTagName("a");
        if (links.length > 0) {
            var href = links[0].href.toLowerCase();

            if (! (href.endsWith(".jpg") || href.endsWith(".jpeg") || href.endsWith(".png") ||
                   href.endsWith(".svg"))){
                return;
            }
        }

        imgs[0].onclick = function (event) {
            if (event.stopPropagation)
                event.stopPropagation();
            if (window.event)
                window.event.cancelBubble = true;

            var modal_html = "<div id=\"myModal\" class=\"modal\">\
  <span class=\"close\" id=\"modal_close\">&times;</span>\
  <img class=\"modal-content\" id=\"modal_image\">\
  <div id=\"caption_text\"></div>\
</div>";
            document.body.innerHTML += modal_html;

            var modal_element = document.getElementById("myModal");
            var modal_image = document.getElementById("modal_image");

            modal_element.style.display = "block";

            if (links.length > 0) {
                modal_image.src = links[0].href;
            } else {
                var img = figure.getElementsByTagName("img");
                modal_image.src = img.src;
            }

            var caption_text = document.getElementById("caption_text");
            var figcaption = figure.getElementsByTagName("figcaption");
            if (figcaption.length > 0) {
                caption_text.innerHTML = figcaption[0].innerHTML;
            }

            var modal_close = document.getElementById("modal_close");
            modal_close.onclick = function() {
                modal_element.style.display = "none";
                modal_element.outerHTML = "";
            };
            modal_element.onclick = modal_close.onclick;
            modal_image.onclick = function (modal_event) {
                if (modal_event.stopPropagation)
                    modal_event.stopPropagation();
                if (window.event)
                    window.event.cancelBubble = true;
            };

            add_image_overlays();

            return false;
        }
    });
}

function on_body_load() {
    add_twitter_link();
    add_image_overlays();
}
