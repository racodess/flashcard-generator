import json
import urllib.request
from rich.console import Console
from rich.pretty import pprint

console = Console()


def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    request_json = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(
        urllib.request.Request('http://127.0.0.1:8765', request_json)
    ))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def ensure_model_exists():
    model_name = "AnkiConnect: Test"
    existing_models = invoke("modelNames")
    if model_name in existing_models:
        console.log(f"Model '{model_name}' already exists.")
        return

    console.log(f"Model '{model_name}' not found. Creating it...")

    fields = [
        "Name",
        "Front",
        "Back",
        "Example",
        "Citation",
        "Source",
        "Image",
        "external_source",
        "external_page"
    ]

    front_template = """<script>
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

	function render() {
		renderMath("name");
		markdown("name");
		renderMath("front");
		markdown("front");
		show();
	}

	function show() {
		document.getElementById("name").style.visibility = "visible";
		document.getElementById("front").style.visibility = "visible";
		document.getElementById("back").style.visibility = "visible";
		document.getElementById("example").style.visibility = "visible";
		document.getElementById("source").style.visibility = "visible";
		document.getElementById("external_source").style.visibility = "visible";
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
</script>
"""
    back_template = """{{FrontSide}}

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

{{#Source}}<br><br><div id="source" style='text-align: left'><pre>{{Source}}</pre></div>{{/Source}}

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

	function render() {
		renderMath("name");
		markdown("name");
		renderMath("front");
		markdown("front");
		renderMath("back");
		markdown("back");
		renderMath("example");
		markdown("example");
		renderMath("source");
		markdown("source");
		show();
	}

	function show() {
		document.getElementById("name").style.visibility = "visible";
		document.getElementById("front").style.visibility = "visible";
		document.getElementById("back").style.visibility = "visible";
		document.getElementById("example").style.visibility = "visible";
		document.getElementById("source").style.visibility = "visible";
		document.getElementById("external_source").style.visibility = "visible";
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
</script>
"""

    card_templates = [{
        "Name": "Card 1",
        "Front": front_template,
        "Back": back_template
    }]

    css = """.card {
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
		font-family: monospace;
		font-weight: 500;
}

.container {
		display: flex;
		justify-content: center;
}

.ex-break {
		width: 50%;
}
"""

    invoke("createModel", modelName=model_name, inOrderFields=fields, cardTemplates=card_templates, css=css)
    console.log(f"Model '{model_name}' created successfully.")


def add_flashcards_to_anki(flashcards, deck_name="Default"):
    ensure_model_exists()

    notes = []
    for fc in flashcards:
        fields = {
            "Name": fc.name,
            "Front": fc.front,
            "Back": fc.back,
            "Example": fc.example,
            "Citation": fc.citation,
            "Source": fc.source,
            "Image": fc.image,
            "external_source": fc.external_source,
            "external_page": str(fc.external_page),
        }

        note = {
            "deckName": deck_name,
            "modelName": "AnkiConnect: Test",
            "fields": fields,
            "options": {
                "allowDuplicate": True
            },
            "tags": fc.tags
        }
        notes.append(note)

    result = invoke("addNotes", notes=notes)
    console.log("Notes added with IDs:", result)