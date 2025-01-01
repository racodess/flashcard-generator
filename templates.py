"""
Purpose:

- Contains the HTML or CSS markup used by Anki "note types" (flashcard templates).
"""
BASIC_CARD_NAME = "AnkiConnect: Basic"

PROBLEM_CARD_NAME = "AnkiConnect: Problem"

# TODO: Add URL field
BASIC_TEMPLATE_FIELDS = [
    "Header",
    "Front",
    "Back",
    "Example",
    "Image",
    "external_source",
    "external_page"
]

# TODO: Add URL field
PROBLEM_TEMPLATE_FIELDS = [
    "Header",
    "Problem",
    "URL",
    "Approach",
    "Solution",
    "Time",
    "Time Explanation",
    "Space",
    "Space Explanation",
    "Step 1",
    "Code 1",
    "Pitfall 1",
    "Step 2",
    "Code 2",
    "Pitfall 2",
    "Step 3",
    "Code 3",
    "Pitfall 3",
    "Step 4",
    "Code 4",
    "Pitfall 4",
    "Step 5",
    "Code 5",
    "Pitfall 5",
    "Step 6",
    "Code 6",
    "Pitfall 6",
    "Step 7",
    "Code 7",
    "Pitfall 7",
    "Step 8",
    "Code 8",
    "Pitfall 8",
    "Step 9",
    "Code 9",
    "Pitfall 9",
    "Image",
    "external_source",
    "external_page"
]

BASIC_CSS = r""".card {
    font-family: arial;
    font-size: 	16px;
		line-height: 1.5;
    text-align: center;
    color: black;
    background-color: white;
}

table, th, td {
	border: 1px solid black;
	border-collapse: collapse;
}

#front, #back, #extra {
	visibility: hidden;
}

pre code {
  background-color: #eee;
  border: 1px solid #999;
  display: block;
  padding: 20px;
  overflow: auto;
}

@media (max-width: 767px) {
    .card {
        font-size: 12px;
    }
}

li {
    margin-top: 10px;
}

code {
    padding-left: 3px;
    padding-right: 3px;
    margin-left: 2px;
    margin-right: 2px;
    border-radius: 3px;
    background-color: #ecf0f1;
    font-family: Consolas, SF Mono, DejaVu Sans Mono, Roboto Mono, monospace;
    font-weight: 500;
}

.container {
    display: flex;
    justify-content: center;
}

.ex-break {
    width: 50%;
}

#steps li {
    margin: 30px;
}
"""

ADDITIONAL_CSS = r"""
@page {
    size: Letter;
    margin: 0.25in;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 20px;
}
th, td {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}
tr:nth-child(even) {
    background-color: #f9f9f9;
}
body {
    font-family: Arial, sans-serif;
    line-height: 1.5;
    color: #2c3e50;
    margin: 0; /* We rely on @page margin for PDF */
}
p {
    margin: 0 0 1em 0;
}
ul, ol {
    margin: 0 0 1em 1.5em;
    padding: 0;
    list-style-position: outside;
}
li {
    margin-bottom: 0.5em;
}
strong {
    font-weight: bold;
    font-size: 1.1em;
}
div.codehilite, pre {
    background-color: #272822; 
    color: #f8f8f2;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    margin: 1em 0;
    font-family: Consolas, "Courier New", Courier, monospace;
    font-size: 0.9em;
    line-height: 1.4;
}
div.codehilite code, pre code {
    background: none;  /* Let the parent div handle background */
    color: inherit;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
}
/* Pygments token classes you may see in the snippet:
   .n (names), .nf (function names), .k (keywords),
   .kd (keyword declarations), .kt (data types), .c1 (comments),
   .mi (numbers), .err (lexing errors), etc.
*/
.n  { color: #a8b3ab; }     /* Generic text/name */
.nf { color: #66d9ef; }     /* Function name */
.k  { color: #66d9ef; }     /* Keyword */
.kd { color: #66d9ef; }     /* Keyword declaration (e.g., 'public', 'class') */
.kt { color: #fd971f; }     /* Data type keywords (e.g., int, float) */
.c1 { color: #75715e; font-style: italic; }  /* Comment */
.mi { color: #ae81ff; }     /* Number (int, float literals) */
.err { color: #ff0000; }    /* Anything flagged as an error token */
code {
    background-color: #f5f5f5;
    color: #c7254e;
    font-family: Consolas, "Courier New", Courier, monospace;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}
"""

MARKDOWN_KATEX_SCRIPT = r"""
<script>
	var getResources = [
		getCSS("_katex.css", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"),
		getCSS("_highlight.css", "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.0.1/styles/default.min.css"),
		getScript("_highlight.js", "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.0.1/highlight.min.js"),
		getScript("_katex.min.js", "https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"),
		getScript("_auto-render.js", "https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/auto-render-cdn.js"),
		getScript("_markdown-it.min.js", "https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.0.4/markdown-it.min.js"),
		getScript("_markdown-it-mark.js","https://cdn.jsdelivr.net/gh/Jwrede/Anki-KaTeX-Markdown/_markdown-it-mark.js")
	];
        Promise.all(getResources).then(() => getScript("_mhchem.js", "https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/contrib/mhchem.min.js")).then(render).catch(show);
	function getScript(path, altURL) {
		return new Promise((resolve, reject) => {
			let script = document.createElement("script");
			script.onload = resolve;
			script.onerror = function() {
				let script_online = document.createElement("script");
				script_online.onload = resolve;
				script_online.onerror = reject;
				script_online.src = altURL;
				document.head.appendChild(script_online);
			}
			script.src = path;
			document.head.appendChild(script);
		})
	}
	function getCSS(path, altURL) {
		return new Promise((resolve, reject) => {
			var css = document.createElement('link');
			css.setAttribute('rel', 'stylesheet');
			css.type = 'text/css';
			css.onload = resolve;
			css.onerror = function() {
				var css_online = document.createElement('link');
				css_online.setAttribute('rel', 'stylesheet');
				css_online.type = 'text/css';
				css_online.onload = resolve;
				css_online.onerror = reject;
				css_online.href = altURL;
				document.head.appendChild(css_online);
			}
			css.href = path;
			document.head.appendChild(css);
		});
	}
	function renderMath(ID) {
		let text = document.getElementById(ID).innerHTML;
		text = replaceInString(text);
		document.getElementById(ID).textContent = text;
		renderMathInElement(document.getElementById(ID), {
			delimiters:  [
  				{left: "$$", right: "$$", display: true},
  				{left: "$", right: "$", display: false}
			],
                        throwOnError : false
		});
	}
	function markdown(ID) {
		let md = new markdownit({typographer: true, html:true, highlight: function (str, lang) {
                            if (lang && hljs.getLanguage(lang)) {
                                try {
                                    return hljs.highlight(str, { language: lang }).value;
                                } catch (__) {}
                            }

                            return ''; // use external default escaping
                        }}).use(markdownItMark);
		let text = replaceHTMLElementsInString(document.getElementById(ID).innerHTML);
		text = md.render(text);
		document.getElementById(ID).innerHTML = text.replace(/&lt;\/span&gt;/gi,"\\");
	}
	function replaceInString(str) {
		str = str.replace(/<[\/]?pre[^>]*>/gi, "");
		str = str.replace(/<br\s*[\/]?[^>]*>/gi, "\n");
		str = str.replace(/<div[^>]*>/gi, "\n");
		// Thanks Graham A!
		str = str.replace(/<[\/]?span[^>]*>/gi, "")
		str.replace(/<\/div[^>]*>/g, "\n");
		return replaceHTMLElementsInString(str);
	}
	function replaceHTMLElementsInString(str) {
		str = str.replace(/&nbsp;/gi, " ");
		str = str.replace(/&tab;/gi, "	");
		str = str.replace(/&gt;/gi, ">");
		str = str.replace(/&lt;/gi, "<");
		return str.replace(/&amp;/gi, "&");
	}
"""

BASIC_FRONT_MAIN = r"""
{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u><br><br></pre></div>{{/Header}}

<div id="front"><pre>{{Front}}</pre></div>
"""

BASIC_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("front");
    markdown("front");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("front").style.visibility = "visible";
}
</script>
"""

BASIC_FRONT_TEMPLATE = BASIC_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + BASIC_FRONT_SCRIPT

BASIC_BACK_MAIN = r"""
{{FrontSide}}

<hr id=answer>

<div id="back"><pre>{{Back}}</pre></div>

{{#Example}}<br><br><div id="example"><pre>{{Example}}</pre></div>{{/Example}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

BASIC_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("front");
    markdown("front");
    renderMath("back");
    markdown("back");
    renderMath("example");
    markdown("example");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("front").style.visibility = "visible";
    document.getElementById("back").style.visibility = "visible";
    document.getElementById("example").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

BASIC_BACK_TEMPLATE = BASIC_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + BASIC_BACK_SCRIPT

PROBLEM_APPROACH_FRONT_MAIN = r"""
{{#Approach}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

What is the <strong>high-level logic</strong> of this approach?

{{/Approach}}
"""

PROBLEM_APPROACH_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
}
</script>
"""

PROBLEM_APPROACH_FRONT_TEMPLATE = PROBLEM_APPROACH_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_APPROACH_FRONT_SCRIPT

PROBLEM_APPROACH_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

What is the <strong>high-level logic</strong> of this approach?

<br><br>
<hr id='answer' />

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_APPROACH_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_APPROACH_BACK_TEMPLATE = PROBLEM_APPROACH_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_APPROACH_BACK_SCRIPT

PROBLEM_TIME_SPACE_FRONT_MAIN = r"""
{{#Approach}}
{{#Time}}
{{#Space}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<div id="solution"><pre><br><br>{{Solution}}</pre></div>

What is the <strong>complexity analysis</strong> of this approach?

{{/Space}}
{{/Time}}
{{/Approach}}
"""

PROBLEM_TIME_SPACE_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
}
</script>
"""

PROBLEM_TIME_SPACE_FRONT_TEMPLATE = PROBLEM_TIME_SPACE_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_TIME_SPACE_FRONT_SCRIPT

PROBLEM_TIME_SPACE_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<div id="solution"><pre><br><br>{{Solution}}</pre></div>

<br><br>

What is the <strong>complexity analysis</strong> of this approach?

<br><br>
<hr id='answer'>

<ul id='steps'>

<li>
<div id="time"><pre><br><br><strong>Time Complexity:</strong> ${{Time}}$</pre></div>
{{#Time Explanation}}<div id="time_explanation"><pre><br><br>{{Time Explanation}}</pre></div>{{/Time Explanation}}
</li>

<li>
<div id="space"><pre><br><br><strong>Space Complexity:</strong> ${{Space}}$</pre></div>
{{#Space Explanation}}<div id="space_explanation"><pre><br><br>{{Space Explanation}}</pre></div>{{/Space Explanation}}
</li>

<ul>

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_TIME_SPACE_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("time");
    markdown("time");
    renderMath("time_explanation");
    markdown("time_explanation");
    renderMath("space");
    markdown("space");
    renderMath("space_explanation");
    markdown("space_explanation");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("time").style.visibility = "visible";
    document.getElementById("time_explanation").style.visibility = "visible";
    document.getElementById("space").style.visibility = "visible";
    document.getElementById("space_explanation").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_TIME_SPACE_BACK_TEMPLATE = PROBLEM_TIME_SPACE_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_TIME_SPACE_BACK_SCRIPT

PROBLEM_PITFALLS_FRONT_MAIN = r"""
{{#Approach}}
{{#Solution}}
{{#Pitfall 1}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<div id="solution"><pre><br><br>{{Solution}}</pre></div>

<br><br>

What are the <strong>pitfalls</strong> of this approach's implementation?

{{/Pitfall 1}}
{{/Solution}}
{{/Approach}}
"""

PROBLEM_STEP1_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>first</strong> step of this approach?

{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP1_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP1_FRONT_TEMPLATE = PROBLEM_STEP1_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP1_FRONT_SCRIPT

PROBLEM_STEP1_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>first</strong> step of this approach?

<br><br>
<hr id='answer'>

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Pitfall 1}}<div id="pitfall1"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 1}}</pre></div>{{/Pitfall 1}}
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP1_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("pitfall1");
    markdown("pitfall1");
    renderMath("code1");
    markdown("code1");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("pitfall1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP1_BACK_TEMPLATE = PROBLEM_STEP1_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP1_BACK_SCRIPT

PROBLEM_STEP2_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

</ol>

{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP2_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP2_FRONT_TEMPLATE = PROBLEM_STEP2_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP2_FRONT_SCRIPT

PROBLEM_STEP2_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Pitfall 2}}<div id="pitfall2"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 2}}</pre></div>{{/Pitfall 2}}
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP2_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("pitfall2");
    markdown("pitfall2");
    renderMath("code2");
    markdown("code2");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("pitfall2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP2_BACK_TEMPLATE = PROBLEM_STEP2_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP2_BACK_SCRIPT

PROBLEM_STEP3_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

</ol>

{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP3_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP3_FRONT_TEMPLATE = PROBLEM_STEP3_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP3_FRONT_SCRIPT

PROBLEM_STEP3_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Pitfall 3}}<div id="pitfall3"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 3}}</pre></div>{{/Pitfall 3}}
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP3_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("pitfall3");
    markdown("pitfall3");
    renderMath("code3");
    markdown("code3");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("pitfall3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP3_BACK_TEMPLATE = PROBLEM_STEP3_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP3_BACK_SCRIPT

PROBLEM_STEP4_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

</ol>

{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP4_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP4_FRONT_TEMPLATE = PROBLEM_STEP4_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP4_FRONT_SCRIPT

PROBLEM_STEP4_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Pitfall 4}}<div id="pitfall4"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 4}}</pre></div>{{/Pitfall 4}}
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP4_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("pitfall4");
    markdown("pitfall4");
    renderMath("code4");
    markdown("code4");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("pitfall4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP4_BACK_TEMPLATE = PROBLEM_STEP4_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP4_BACK_SCRIPT

PROBLEM_STEP5_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}
{{#Step 5}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

</ol>

{{/Step 5}}
{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP5_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP5_FRONT_TEMPLATE = PROBLEM_STEP5_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP5_FRONT_SCRIPT

PROBLEM_STEP5_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Pitfall 5}}<div id="pitfall5"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 5}}</pre></div>{{/Pitfall 5}}
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>


</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP5_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("pitfall5");
    markdown("pitfall5");
    renderMath("code5");
    markdown("code5");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("pitfall5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP5_BACK_TEMPLATE = PROBLEM_STEP5_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP5_BACK_SCRIPT

PROBLEM_STEP6_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}
{{#Step 5}}
{{#Step 6}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>


</ol>

{{/Step 6}}
{{/Step 5}}
{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP6_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP6_FRONT_TEMPLATE = PROBLEM_STEP6_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP6_FRONT_SCRIPT

PROBLEM_STEP6_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Pitfall 6}}<div id="pitfall6"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 6}}</pre></div>{{/Pitfall 6}}
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>


</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP6_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("pitfall6");
    markdown("pitfall6");
    renderMath("code6");
    markdown("code6");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("pitfall6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP6_BACK_TEMPLATE = PROBLEM_STEP6_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP6_BACK_SCRIPT

PROBLEM_STEP7_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}
{{#Step 5}}
{{#Step 6}}
{{#Step 7}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>


</ol>

{{/Step 7}}
{{/Step 6}}
{{/Step 5}}
{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP7_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP7_FRONT_TEMPLATE = PROBLEM_STEP7_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP7_FRONT_SCRIPT

PROBLEM_STEP7_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step7"><pre><br><br>{{Step 7}}</pre></div>
{{#Pitfall 7}}<div id="pitfall7"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 7}}</pre></div>{{/Pitfall 7}}
{{#Code 7}}<div id="code7"><pre><br><br>{{Code 7}}</pre></div>{{/Code 7}}
</li>


</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP7_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("step7");
    markdown("step7");
    renderMath("pitfall7");
    markdown("pitfall7");
    renderMath("code7");
    markdown("code7");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("step7").style.visibility = "visible";
    document.getElementById("pitfall7").style.visibility = "visible";
    document.getElementById("code7").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP7_BACK_TEMPLATE = PROBLEM_STEP7_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP7_BACK_SCRIPT

PROBLEM_STEP8_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}
{{#Step 5}}
{{#Step 6}}
{{#Step 7}}
{{#Step 8}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>

<li>
<div id="step7"><pre><br><br>{{Step 7}}</pre></div>
{{#Code 7}}<div id="code7"><pre><br><br>{{Code 7}}</pre></div>{{/Code 7}}
</li>


</ol>

{{/Step 8}}
{{/Step 7}}
{{/Step 6}}
{{/Step 5}}
{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP8_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("step7");
    markdown("step7");
    renderMath("code7");
    markdown("code7");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("step7").style.visibility = "visible";
    document.getElementById("code7").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP8_FRONT_TEMPLATE = PROBLEM_STEP8_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP8_FRONT_SCRIPT

PROBLEM_STEP8_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>

<li>
<div id="step7"><pre><br><br>{{Step 7}}</pre></div>
{{#Code 7}}<div id="code7"><pre><br><br>{{Code 7}}</pre></div>{{/Code 7}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step8"><pre><br><br>{{Step 8}}</pre></div>
{{#Pitfall 8}}<div id="pitfall8"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 8}}</pre></div>{{/Pitfall 8}}
{{#Code 8}}<div id="code8"><pre><br><br>{{Code 8}}</pre></div>{{/Code 8}}
</li>


</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}

{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP8_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("step7");
    markdown("step7");
    renderMath("code7");
    markdown("code7");
    renderMath("step8");
    markdown("step8");
    renderMath("pitfall8");
    markdown("pitfall8");
    renderMath("code8");
    markdown("code8");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("step7").style.visibility = "visible";
    document.getElementById("code7").style.visibility = "visible";
    document.getElementById("step8").style.visibility = "visible";
    document.getElementById("pitfall8").style.visibility = "visible";
    document.getElementById("code8").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP8_BACK_TEMPLATE = PROBLEM_STEP8_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP8_BACK_SCRIPT

PROBLEM_STEP9_FRONT_MAIN = r"""
{{#Approach}}
{{#Step 1}}
{{#Step 2}}
{{#Step 3}}
{{#Step 4}}
{{#Step 5}}
{{#Step 6}}
{{#Step 7}}
{{#Step 8}}
{{#Step 9}}

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}


{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<br><br>

<br><br>
<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>

<li>
<div id="step7"><pre><br><br>{{Step 7}}</pre></div>
{{#Code 7}}<div id="code7"><pre><br><br>{{Code 7}}</pre></div>{{/Code 7}}
</li>

<li>
<div id="step8"><pre><br><br>{{Step 8}}</pre></div>
{{#Code 8}}<div id="code8"><pre><br><br>{{Code 8}}</pre></div>{{/Code 8}}
</li>


</ol>

{{/Step 9}}
{{/Step 8}}
{{/Step 7}}
{{/Step 6}}
{{/Step 5}}
{{/Step 4}}
{{/Step 3}}
{{/Step 2}}
{{/Step 1}}
{{/Approach}}
"""

PROBLEM_STEP9_FRONT_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("step7");
    markdown("step7");
    renderMath("code7");
    markdown("code7");
    renderMath("step8");
    markdown("step8");
    renderMath("code8");
    markdown("code8");
    renderMath("solution");
    markdown("solution");
    show();
}

function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("step7").style.visibility = "visible";
    document.getElementById("code7").style.visibility = "visible";
    document.getElementById("step8").style.visibility = "visible";
    document.getElementById("code8").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP9_FRONT_TEMPLATE = PROBLEM_STEP9_FRONT_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP9_FRONT_SCRIPT

PROBLEM_STEP9_BACK_MAIN = r"""

{{#URL}}<a href='{{URL}}' style='text-decoration: underline; font-size: 10px;'>{{Problem}}</a>{{/URL}}

{{#Header}}<div id="header"><pre><strong><u>{{Header}}</strong></u></pre></div>{{/Header}}

<br><br>

<div id="approach"><pre><br><br>{{Approach}}</pre></div>

<br><br>

What is the <strong>next</strong> step of this approach?

<ol id='steps'>

<li>
<div id="step1"><pre><br><br>{{Step 1}}</pre></div>
{{#Code 1}}<div id="code1"><pre><br><br>{{Code 1}}</pre></div>{{/Code 1}}
</li>

<li>
<div id="step2"><pre><br><br>{{Step 2}}</pre></div>
{{#Code 2}}<div id="code2"><pre><br><br>{{Code 2}}</pre></div>{{/Code 2}}
</li>

<li>
<div id="step3"><pre><br><br>{{Step 3}}</pre></div>
{{#Code 3}}<div id="code3"><pre><br><br>{{Code 3}}</pre></div>{{/Code 3}}
</li>

<li>
<div id="step4"><pre><br><br>{{Step 4}}</pre></div>
{{#Code 4}}<div id="code4"><pre><br><br>{{Code 4}}</pre></div>{{/Code 4}}
</li>

<li>
<div id="step5"><pre><br><br>{{Step 5}}</pre></div>
{{#Code 5}}<div id="code5"><pre><br><br>{{Code 5}}</pre></div>{{/Code 5}}
</li>

<li>
<div id="step6"><pre><br><br>{{Step 6}}</pre></div>
{{#Code 6}}<div id="code6"><pre><br><br>{{Code 6}}</pre></div>{{/Code 6}}
</li>

<li>
<div id="step7"><pre><br><br>{{Step 7}}</pre></div>
{{#Code 7}}<div id="code7"><pre><br><br>{{Code 7}}</pre></div>{{/Code 7}}
</li>

<li>
<div id="step8"><pre><br><br>{{Step 8}}</pre></div>
{{#Code 8}}<div id="code8"><pre><br><br>{{Code 8}}</pre></div>{{/Code 8}}
</li>

<br>
<hr id='answer'>
<br>

<li>
<div id="step9"><pre><br><br>{{Step 9}}</pre></div>
{{#Pitfall 9}}<div id="pitfall9"><pre><br><br><strong>Pitfall:</strong> {{Pitfall 9}}</pre></div>{{/Pitfall 9}}
{{#Code 9}}<div id="code9"><pre><br><br>{{Code 9}}</pre></div>{{/Code 9}}
</li>


</ol>

{{#Solution}}<br><div id="solution"><pre>{{Solution}}</pre></div>{{/Solution}}


{{#Image}}<br><br><div id="image"><pre><img src="{{Image}}" /></pre></div>{{/Image}}

{{#external_source}}
<br><br>
<a class="pdfjsaddon_twofields" onclick="send_pdf_info_back(); return false" href="#">Source: {{text:external_source}}</a>
<script src="_js_base64_minified_for_pdf_viewer_addon.js"></script>
<script>
function send_pdf_info_back(){
    var pdf_viewer_helper__encoded = Base64.encode("{{text:external_source}}");
    var merged_pdf_addon = `pdfjs319501851${pdf_viewer_helper__encoded}319501851{{text:external_page}}`;
    pycmd(merged_pdf_addon);
}
</script>
{{/external_source}}
"""

PROBLEM_STEP9_BACK_SCRIPT = r"""
function render() {
    renderMath("header");
    markdown("header");
    renderMath("approach");
    markdown("approach");
    renderMath("step1");
    markdown("step1");
    renderMath("code1");
    markdown("code1");
    renderMath("step2");
    markdown("step2");
    renderMath("code2");
    markdown("code2");
    renderMath("step3");
    markdown("step3");
    renderMath("code3");
    markdown("code3");
    renderMath("step4");
    markdown("step4");
    renderMath("code4");
    markdown("code4");
    renderMath("step5");
    markdown("step5");
    renderMath("code5");
    markdown("code5");
    renderMath("step6");
    markdown("step6");
    renderMath("code6");
    markdown("code6");
    renderMath("step7");
    markdown("step7");
    renderMath("code7");
    markdown("code7");
    renderMath("step8");
    markdown("step8");
    renderMath("code8");
    markdown("code8");
    renderMath("step9");
    markdown("step9");
    renderMath("pitfall9");
    markdown("pitfall9");
    renderMath("code9");
    markdown("code9");
    renderMath("solution");
    markdown("solution");
    show();
}
function show() {
    document.getElementById("header").style.visibility = "visible";
    document.getElementById("approach").style.visibility = "visible";
    document.getElementById("step1").style.visibility = "visible";
    document.getElementById("code1").style.visibility = "visible";
    document.getElementById("step2").style.visibility = "visible";
    document.getElementById("code2").style.visibility = "visible";
    document.getElementById("step3").style.visibility = "visible";
    document.getElementById("code3").style.visibility = "visible";
    document.getElementById("step4").style.visibility = "visible";
    document.getElementById("code4").style.visibility = "visible";
    document.getElementById("step5").style.visibility = "visible";
    document.getElementById("code5").style.visibility = "visible";
    document.getElementById("step6").style.visibility = "visible";
    document.getElementById("code6").style.visibility = "visible";
    document.getElementById("step7").style.visibility = "visible";
    document.getElementById("code7").style.visibility = "visible";
    document.getElementById("step8").style.visibility = "visible";
    document.getElementById("code8").style.visibility = "visible";
    document.getElementById("step9").style.visibility = "visible";
    document.getElementById("pitfall9").style.visibility = "visible";
    document.getElementById("code9").style.visibility = "visible";
    document.getElementById("solution").style.visibility = "visible";
    document.getElementById("external_source").style.visibility = "visible";
}
</script>
"""

PROBLEM_STEP9_BACK_TEMPLATE = PROBLEM_STEP9_BACK_MAIN + MARKDOWN_KATEX_SCRIPT + PROBLEM_STEP9_BACK_SCRIPT