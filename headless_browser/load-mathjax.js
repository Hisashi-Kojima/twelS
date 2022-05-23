// about loading MathJax, see the below link.
// https://github.com/mathjax/MathJax-demos-web/blob/master/load-mathjax/load-mathjax.html.md

/**
 * load MathJax in the page.
 * @returns {Boolean} - return true when the page uses MathJax.
 */
load_mathjax = function () {
    if (document.body.querySelector('math') ||
        document.body.textContent.match(/(?:\$|\\\(|\\\[|\\begin\{.*?})/)) {
      if (!window.MathJax) {
        window.MathJax = {
          tex: {
            inlineMath: {'[+]': [['$', '$']]}
          }
        };
      }
      var script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
      document.head.appendChild(script);
      return true;
    } else {
      return false;
    }
}