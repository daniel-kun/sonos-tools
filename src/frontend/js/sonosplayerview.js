import React from 'react';
import ReactDOM from 'react-dom';

function sonosPlayTest(apiKey, language, text)
{
    var loc = window.location
    var speakApiUri = `${loc.protocol}//${loc.host}/api/v1/speak`
    console.log(speakApiUri)
    fetch(speakApiUri, {
        method: "POST",
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"text": text, "languagecode": language, "key": apiKey})
    }).then(response => console.log(response))
}

export class SonosPlayerView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            testText: 'I am alive!',
            language: 'en-US',
            previewExpanded: false
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
        sonosPlayTest(this.props.player.apiKey, this.state.language, this.state.testText)
        ev.preventDefault()
    }

    toggleExpandHTTP(ev) {
        this.setState( Object.assign(this.state, {
            previewExpanded: !this.state.previewExpanded
        }));
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

        var preview = 
`POST /api/v1/speak HTTP/1.1
Host: sonos-tools.from-anywhere.com
Content-Type: application/json

{
   "text": "${this.state.testText}",
   "languagecode": "${this.state.language}",
   "key": "${this.props.player.apiKey}"
}`
        return (
            <tr>
                <td>
                    <p className="player-name">Player „{'name' in this.props.player ? this.props.player.name : this.props.player.playerId}”</p>
                    <form onSubmit={this.handleSubmit.bind(this)}>
                        <input type="text" value={this.state.testText} onChange={this.handleChangeTestText.bind(this)}/>
                        <select value={this.state.language} onChange={this.handleChangeLanguage.bind(this)}>
                            {supportedLanguages.map(lang => <option key={`lang_${lang.language}`} value={lang.language}>{lang.name}</option>)}
                        </select>
                        <input type="submit" className="sonos test-button" value="Test now!"/>
                    </form>
                    <div className="preview">
                        {!this.state.previewExpanded && <a href='#' onClick={this.toggleExpandHTTP.bind(this)}>Show web request</a>}
                        {this.state.previewExpanded && <a href='#' onClick={this.toggleExpandHTTP.bind(this)}>Hide web request</a>}
                        {this.state.previewExpanded && <pre className="code">{preview} </pre>}
                    </div>
                </td>
            </tr>)
    }

}

