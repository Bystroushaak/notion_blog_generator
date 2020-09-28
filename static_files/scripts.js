function get_meta(meta_name) {
  const metas = document.getElementsByTagName('meta');

  for (let i = 0; i < metas.length; i++) {
    if (metas[i].getAttribute('name') === meta_name) {
      return metas[i].getAttribute('content');
    }
  }

  return '';
}


function add_twitter_link() {
    var blog_url = encodeURIComponent(document.location);
    var blog_title = encodeURIComponent(document.title + "\n\n");
    var url = "https://twitter.com/intent/tweet?text=" + blog_title + "&url=" + blog_url;

    var keywords = get_meta('keywords');
    if (keywords) {
        url = url + "&hashtags=" + encodeURIComponent(keywords);
    }

    var twitter_link = document.getElementById("twitter_button");
    if (twitter_link == null) {
        return;
    }

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

            if (href.startsWith("http://") || href.startsWith("https://")) {
                if (! (href.startsWith("http://blog.rfox.eu") || href.startsWith("https://blog.rfox.eu") ||
                       href.startsWith("http://rfox.eu"))) {
                    return;
                }
            }
        }

        if (!imgs[0].src.includes("_thumb.") && imgs[0].naturalWidth == imgs[0].clientWidth) {
            if (links.length > 0) {
                links[0].outerHTML = links[0].innerHTML;
            }

            imgs[0].style.opacity = "1.0";
            imgs[0].style.cursor = "default";

            return;
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
    add_image_overlays();
    add_twitter_link();
}
