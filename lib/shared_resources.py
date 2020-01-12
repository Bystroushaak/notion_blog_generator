import os

class SharedResources:
    def __init__(self, blog_root):
        self.css = ""
        self._css_path = "style.css"
        self._blog_root = blog_root
        self.all_pages = {}
        self.title_map = None

        # sigh, notion uses index page as sort of fake root, this is the real one
        self._real_blog_root = None

    def add_css(self, css):
        self.css = css

        self.css += """
.corner-ribbon{
  width: 14em;
  background: #e43;
  position: absolute;
  text-align: center;
  line-height: 2.5em;
  letter-spacing: 1px;
  color: #f0f0f0;
  transform: rotate(-45deg);
  -webkit-transform: rotate(-45deg);
  position: fixed;
  box-shadow: 0 0 3px rgba(0,0,0,.3);
}

.corner-ribbon.top-right{
  top: 2.8em;
  right: -3em;
  left: auto;
  transform: rotate(45deg);
  -webkit-transform: rotate(45deg);
}

.corner-ribbon.bottom-right{
  top: auto;
  right: -50px;
  bottom: 25px;
  left: auto;
  transform: rotate(-45deg);
  -webkit-transform: rotate(-45deg);
}

.corner-ribbon.red{background: #e43;}

pre {
 white-space: pre-wrap;       /* css-3 */
 white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
 white-space: -pre-wrap;      /* Opera 4-6 */
 white-space: -o-pre-wrap;    /* Opera 7 */
 word-wrap: break-word;       /* Internet Explorer 5.5+ */
}

figure iframe {
    height: 550px;
}

#sidebar_top {
    visibility: hidden;
    height: 0;
}
#sidebar_bottom {
    margin-top: 7em;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
}
@media only screen and (min-width: 1800px) {
    #sidebar_top {
        width: 25em;
        height: auto;

        float: right;
        visibility: visible;
        position: -webkit-sticky;
        position: sticky;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
		font-size: small;

        top: 0;
        margin-top: 11em;
        padding-top: 1em;
        margin-right: -35em;
    }
    #sidebar_bottom {
        visibility: hidden;
    }
}

.twitter-share-button {
    float: right;
    visibility: hidden;
}

.twitter-share-button img {
    width: 5em;
}

@media screen and (max-width: 1000px) {
    body {
        font-size: 40px;
    }
    h1 {
        font-size: 1.875em;
    }
    h2 {
        font-size: 1.5em;
    }
    h3 {
        font-size: 1.25em;
    }
    .twitter-share-button img {
        width: 3.5em;
    }
    .corner-ribbon, .corner-ribbon.top-right{
      font-size: 25px;
    }
}

figure.image img {
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
}

figure.image img:hover {opacity: 0.7;}


/* The Modal (background) */
.modal {
  display: none; /* Hidden by default */
  position: fixed; /* Stay in place */
  z-index: 1; /* Sit on top */
  padding-top: 100px; /* Location of the box */
  left: 0;
  top: 0;
  width: 100%; /* Full width */
  height: 100%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgb(0,0,0); /* Fallback color */
  background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
}

/* Modal Content (image) */
.modal-content {
  margin: auto;
  display: block;
  /*width: 80%;*/
  /*max-width: 700px;*/
}

/* Caption of Modal Image */
#caption_text {
  margin: auto;
  display: block;
  width: 80%;
  max-width: 700px;
  text-align: center;
  color: white;
  padding: 10px 0;
  height: 150px;
}

/* Add Animation */
.modal-content, #caption {  
  -webkit-animation-name: zoom;
  -webkit-animation-duration: 0.3s;
  animation-name: zoom;
  animation-duration: 0.3s;
}

@-webkit-keyframes zoom {
  from {-webkit-transform:scale(0)} 
  to {-webkit-transform:scale(1)}
}

@keyframes zoom {
  from {transform:scale(0)} 
  to {transform:scale(1)}
}

/* The Close Button */
.close {
  position: absolute;
  top: 15px;
  right: 35px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  transition: 0.3s;
}

.close:hover,
.close:focus {
  color: #bbb;
  text-decoration: none;
  cursor: pointer;
}

/* 100% Image Width on Smaller Screens */
@media only screen and (max-width: 700px){
  .modal-content {
    width: 100%;
  }
}
"""

        return self._css_path

    def add_page(self, filename, page):
        """
        Args:
            filename (str):
            page (Page):
        """
        self.all_pages[filename] = page

    def save(self):
        self.css = self.css.replace("white-space: pre-wrap;\n", "", 1)
        with open(os.path.join(self._real_blog_root, self._css_path), "w") as f:
            f.write(self.css.strip() + "\n\n")

    def generate_title_map(self):
        self.title_map = {
            page.title: page
            for page in self.all_pages.values()
        }
