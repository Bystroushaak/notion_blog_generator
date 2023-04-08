var currentFigureIndex = -1;
var figuresList = [];

const modalStyle = document.createElement('style');
modalStyle.innerHTML = `
  .modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.9);
  }
  
  .modal-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 20px; /* Add some padding to avoid image touching the screen edges */
  }

  .modal-content {
    margin: auto;
    display: block;
    margin-top: -60px;
    max-height: calc(100%);
    object-fit: contain;
  }

  .modal-content,
  #caption_text {
    -webkit-animation-name: zoom;
    -webkit-animation-duration: 0.6s;
    animation-name: zoom;
    animation-duration: 0.6s;
  }

  @-webkit-keyframes zoom {
    from {
      -webkit-transform: scale(0);
    }
    to {
      -webkit-transform: scale(1);
    }
  }

  @keyframes zoom {
    from {
      transform: scale(0);
    }
    to {
      transform: scale(1);
    }
  }
`;
document.head.appendChild(modalStyle);

const captionStyle = document.createElement('style');
captionStyle.innerHTML = `
  #caption_text {
    margin-top: 0; /* Adjust the top margin to remove space */
  }
`;
document.head.appendChild(captionStyle);

const arrowStyle = document.createElement('style');
arrowStyle.innerHTML = `
  .arrow {
    cursor: pointer;
    position: absolute;
    top: 0;
    bottom: 0;
    width: 50px;
    background-color: rgba(255, 255, 255, 0.5);
    color: white;
    font-weight: bold;
    font-size: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
    transition: background-color 0.6s ease;
  }

  .arrow:hover {
    background-color: rgba(128, 128, 128, 0.8);
  }

  .prev {
    left: 0;
  }

  .next {
    right: 0;
  }

  .modal-container {
    position: relative;
  }
`;
document.head.appendChild(arrowStyle);

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
    figuresList = Array.prototype.slice.call(figures);

    figuresList.forEach(function (figure, index) {
        if (shouldAddOverlay(figure)) {
            addOverlay(figure, index);
        }
    });
}

function shouldAddOverlay(figure) {
    var imgs = figure.getElementsByTagName("img");
    if (imgs.length === 0) return false;

    var links = figure.getElementsByTagName("a");
    if (links.length > 0) {
        var href = links[0].href.toLowerCase();

        if (!isImage(href)) return false;

        if (!isLocal(href)) return false;
    }

    if (!imgs[0].src.includes("_thumb.") && imgs[0].naturalWidth == imgs[0].clientWidth) {
        if (links.length > 0) {
            links[0].outerHTML = links[0].innerHTML;
        }

        imgs[0].style.opacity = "1.0";
        imgs[0].style.cursor = "default";

        return false;
    }

    return true;
}

function isImage(href) {
    return href.endsWith(".jpg") || href.endsWith(".jpeg") || href.endsWith(".png") || href.endsWith(".svg");
}

function isLocal(href) {
    if (href.startsWith("http://") || href.startsWith("https://")) {
        if (! (href.startsWith("http://blog.rfox.eu") || href.startsWith("https://blog.rfox.eu") ||
               href.startsWith("http://rfox.eu"))) {
            return false;
        }
    }
    return true;
}

function addOverlay(figure, index) {
    var imgs = figure.getElementsByTagName("img");
    imgs[0].onclick = function (event) {
        event.stopPropagation();
        openModal(figure, index);
        return false;
    }
}

function openModal(figure, index) {
    var modal_html = `<div id="myModal" class="modal">
  <span class="close" id="modal_close">&times;</span>
  <div id="counter_text"></div>
  <div id="caption_text"></div>
  <div class="modal-container">
    <div class="modal-content"> <!-- Add the modal-content class here -->
      <img id="modal_image">
      <div id="modal_prev" class="prev arrow">&#10094;</div>
      <div id="modal_next" class="next arrow">&#10095;</div>
    </div>
  </div>
</div>`;
    var parser = new DOMParser();
    var modal_element = parser.parseFromString(modal_html, "text/html").body.firstChild;
    document.body.appendChild(modal_element);

    var modal_image = document.getElementById("modal_image");

    updateModalContent(figure, index, function () {
        setupModalClose(modal_element, modal_image);
        modal_element.style.display = "block";
    });
}

function setCaptionText(figure) {
    var caption_text = document.getElementById("caption_text");
    var counter_text = document.getElementById("counter_text");

    counter_text.style.color = "white";
    counter_text.style.textAlign = "center";

    var figcaption = figure.getElementsByTagName("figcaption");

    if (figcaption.length > 0) {
        caption_text.innerHTML = figcaption[0].innerHTML;
        caption_text.style.display = "block";
    } else {
        caption_text.innerHTML = "";
        caption_text.style.display = "none";
    }

    if (currentFigureIndex >= 0) {
        counter_text.innerHTML = currentFigureIndex + " of " + (figuresList.length - 1);
        counter_text.style.display = "block";
    } else {
        counter_text.style.display = "none";
    }
}

function setupModalClose(modal_element, modal_image) {
    var modal_prev = document.getElementById("modal_prev");
    var modal_next = document.getElementById("modal_next");
    modal_prev.onclick = function (event) {
        event.stopPropagation();
        navigateToPreviousFigure();
    };
    modal_next.onclick = function (event) {
        event.stopPropagation();
        navigateToNextFigure();
    };

    var modal_close = document.getElementById("modal_close");
    modal_close.onclick = function() {
        closeModal(modal_element);
    };
    modal_element.onclick = modal_close.onclick;
    modal_image.onclick = function (modal_event) {
        modal_event.stopPropagation();
        closeModal(modal_element);
    };

    document.onkeydown = function(evt) {
        evt = evt || window.event;
        if (evt.keyCode === 27) {
            closeModal(modal_element);
        } else if (evt.keyCode === 37) {
            navigateToPreviousFigure();
        } else if (evt.keyCode === 39) {
            navigateToNextFigure();
        }
    };
}

function closeModal(modal_element) {
    var modal_image = document.getElementById("modal_image");
    var modal_prev = document.getElementById("modal_prev");
    var modal_next = document.getElementById("modal_next");
    modal_image.onload = null;

    modal_element.style.display = "none";
    document.body.removeChild(modal_element);
    document.body.removeChild(modal_prev); // Remove the left arrow button
    document.body.removeChild(modal_next); // Remove the right arrow button
    currentFigureIndex = -1;
}

function updateModalContent(figure, index, callback) {
    var modal_image = document.getElementById("modal_image");
    var caption_text = document.getElementById("caption_text"); // Add this line

    var links = figure.getElementsByTagName("a");

    if (links.length > 0) {
        modal_image.src = links[0].getAttribute('href');
    } else {
        var img = figure.getElementsByTagName("img");
        modal_image.src = img[0].getAttribute('src');
    }

    caption_text.style.marginTop = "0"; // Add this line to reset the margin-top

    modal_image.onload = function() {
        currentFigureIndex = index;
        setCaptionText(figure);
        callback();
    };
}

function navigateToPreviousFigure() {
    if (currentFigureIndex > 0) {
        updateModalContent(figuresList[currentFigureIndex - 1], currentFigureIndex - 1);
    } else {
        updateModalContent(figuresList[figuresList.length - 1], figuresList.length - 1);
    }
}

function navigateToNextFigure() {
    if (currentFigureIndex < figuresList.length - 1) {
        updateModalContent(figuresList[currentFigureIndex + 1], currentFigureIndex + 1);
    } else {
        updateModalContent(figuresList[0], 0);
    }
}

function on_body_load() {
    add_image_overlays();
    add_twitter_link();
}