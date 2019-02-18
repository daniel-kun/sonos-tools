import React from 'react';
import ReactDOM from 'react-dom';

function speakApiUri()
{
    var loc = window.location
    return `${loc.protocol}//${loc.host}/api/v1/speak`
}

function sonosPlayTest(apiKey, language, text)
{
    fetch(speakApiUri(), {
        method: "POST",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"text": text, "languagecode": language, "key": apiKey})
    }).then(response => console.log(response))
}

function previewHttp(text, languageCode, apiKey)
{
    return (
`POST /api/v1/speak HTTP/1.1
Host: ${window.location.hostname} 
Content-Type: application/json

{
   "text": "${text}",
   "languagecode": "${languageCode}",
   "key": "${apiKey}"
}`)
}

function previewCurl(text, languageCode, apiKey)
{
    return (
`curl ${speakApiUri()} -X POST -H "Content-Type: application/json" --data '{
    "text": "${text}",
    "languagecode": "${languageCode}",
    "key": "${apiKey}"
}';`)
}

function previewJavaScript(text, languageCode, apiKey)
{
    return (
`fetch("${speakApiUri()}", {
    method: "POST",
    cache: "no-cache",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        "text": "${text}",
        "languagecode": "${languageCode}",
        "key": "${apiKey}"
    })
}).then(response => console.log(response))`)
}

function previewCSharp(text, languageCode, apiKey)
{
    return (
`HttpWebRequest request = (HttpWebRequest) WebRequest.Create("${speakApiUri()}");
request.Method = "POST";
request.ContentType = "application/json";
byte[] payload = Encoding.UTF8.GetBytes(@"{
    ""text"": ""${text}"",
    ""languagecode"": ""${languageCode}"",
    ""key"": ""${apiKey}""
}");
request.GetRequestStream().Write(payload, 0, payload.Length);
using (var reader = new StreamReader(request.GetResponse().GetResponseStream()))
{
    string response = reader.ReadToEnd();
}`);
}

function previewPython(text, languageCode, apiKey)
{
    return (
`import requests
r = requests.post("${speakApiUri()}",
        headers={"Content-Type": "application/json"},
        json={
            "text": "${text}",
            "languagecode": "${languageCode}",
            "key": "${apiKey}"
        })
print(r.text)`)
}

var previewModes = [
    { name: 'curl',         renderer: previewCurl },
    { name: 'JavaScript',   renderer: previewJavaScript },
    { name: 'C#',           renderer: previewCSharp },
    { name: 'Python',       renderer: previewPython },
    { name: 'Raw HTTP',     renderer: previewHttp },
]

export class SonosPlayerView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedPlayer: props.players[0],
            selectedPreviewMode: previewModes[0],
            testText: 'Test successful!',
            language: 'en-US'
        }
    }

    handleChangeTestText(ev) {
        this.setState( Object.assign(this.state, {
            testText: ev.target.value
        }));
    }

    handleChangeLanguage(ev) {
        this.setState( Object.assign(this.state, {
            language: ev.target.value
        }));
    }

    handleSubmit(ev) {
        sonosPlayTest(this.state.selectedPlayer.apiKey, this.state.language, this.state.testText)
        ev.preventDefault()
    }

    handleChangeSelectedPlayer(ev) {
        this.setState(Object.assign(this.state, {
            selectedPlayer: ev.target.value
        }));
    }

    selectPreviewMode(mode) {
        console.log(`selecting preview mode ${mode}`)
        this.setState(Object.assign(this.state, {
            selectedPreviewMode: mode
        }));
    }

    renderPreview(mode, state) {
        if (mode) {
            return (<pre>{mode.renderer(state.testText, state.language, state.selectedPlayer.apiKey)}</pre>)
        } else {
            return (<div/>)
        }
    }

    render() {
        var supportedLanguages = [
            { language: 'de-DE', name:  'German' },
            { language: 'en-AU', name:  'English (Australia)' },
            { language: 'en-GB', name:  'English (UK)' },
            { language: 'en-US', name:  'English (US)' },
            { language: 'es-ES', name:  'Spanish' },
            { language: 'fr-CA', name:  'French (Canada)' },
            { language: 'fr-FR', name:  'French' },
            { language: 'it-IT', name:  'Italian' },
            { language: 'ja-JP', name:  'Japanese' },
            { language: 'ko-KR', name:  'Korean' },
            { language: 'nl-NL', name:  'Dutch (Netherlands)' },
            { language: 'pt-BR', name:  'Portugese (Brazil)' },
            { language: 'sv-SE', name:  'Swedish' },
            { language: 'tr-TR', name:  'Turkish' },
        ]

        return (<div className="playerView">
            <form onSubmit={this.handleSubmit.bind(this)}>
                <select value={this.state.selectedPlayer} onChange={this.handleChangeSelectedPlayer.bind(this)}>
                    {this.props.players.map(player => <option key={`player_${player.playerId}`} value={player.apiKey}>{player.name}</option>)}
                </select>
                <input type="text" value={this.state.testText} onChange={this.handleChangeTestText.bind(this)}/>
                <select value={this.state.language} onChange={this.handleChangeLanguage.bind(this)}>
                    {supportedLanguages.map(lang => <option key={`lang_${lang.language}`} value={lang.language}>{lang.name}</option>)}
                </select>
                <input type="submit" className="sonos test-button" value="Test now!"/>
            </form>
            <span>Here's some example code:</span>
            <div className="preview">
                <div className="previewPicker">
                    {previewModes.map(mode => <div key={`preview_${mode.name}`} className={`previewPickerEntry ${mode.name == this.state.selectedPreviewMode.name ? "selected" : ""}`} onClick={this.selectPreviewMode.bind(this, mode)}>{mode.name}</div>)}
                </div>
                <p className="importantNote"><b>Important!</b> Never share your API key with others.</p>
                {this.renderPreview(this.state.selectedPreviewMode, this.state)}
            </div>
        </div>)
    }

}

