import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
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

class SonosPlayerView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            testText: 'I am alive!',
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
        sonosPlayTest(this.props.player.apiKey, this.state.language, this.state.testText)
        ev.preventDefault()
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
                </td>
            </tr>)
    }

}

function renderRoot(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    console.log("renderRoot")
    ReactDOM.render(render(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot), document.getElementById('landing'))
}

function responseGoogleLogin(googleUser)
{
    console.log("responseGoogleLogin")
    // Useful data for your client-side scripts:
    var profile = googleUser.getBasicProfile();
    // The ID token you need to pass to your backend:
    var id_token = googleUser.getAuthResponse().id_token;

    fetch("/receive_google_auth", {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"token": id_token}), // body data type must match "Content-Type" header
    })
    .then(response => response.json())
    .then(json => {
        console.log(json)
        if ("sonos" in json) {
            renderRoot(json, true, json['sonosApiAppKey'], json['redirectUriRoot'])
        } else {
            renderRoot(json, false, json['sonosApiAppKey'], json['redirectUriRoot'])
        }
    });
}

function responseGoogleFailure(error)
{
    console.log(error);
}

function responseGoogleLogout()
{
    renderRoot(null, false);
}

function createSonosAuthUri(clientId, accountid, redirectUri)
{
    var state = window.btoa(JSON.stringify({
                'accountid': accountid
        }))
    return `https://api.sonos.com/login/v3/oauth?client_id=${clientId}&response_type=code&state=${state}&scope=playback-control-all&redirect_uri=${redirectUri}`
}

function sonosLogout(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    fetch("/sonos_logout", {
        method: "POST",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"accountid": account['accountid']}) // TODO: Need stronger authentification here
    })
    .then(response => response.json())
    .then(json => {
        console.log(json)
        renderRoot(account, false, sonosApiAppKey, redirectUriRoot)
    })
    // TODO: Display error message
}

function renderLanding()
{
    return (<div className="landing">
            <h1>SONOS</h1>
            <h2>speaks!</h2>
            <p className="landing-introduction">Integrate your SONOS speakers into your home automation.</p>
            <p className="landing-introduction">Get notified of events, in high fidelity.</p>
            <img className="speaker-left" src="/static/img/sonos-bubble-left.svg"/>
            <img className="speaker-right" src="/static/img/sonos-bubble-right.svg"/>
            
            <GoogleLogin 
                clientId="166334197578-sem3ib4jfiqm8k59npc1s3ddrro5f5bs.apps.googleusercontent.com"
                isSignedIn={true}
                onSuccess={responseGoogleLogin}
                onFailure={responseGoogleFailure}/>
        </div>)
}

function renderLoggedInWithoutSonos(sonosApiAppKey, accountid, redirectUriRoot)
{
    return (<div className="landing">
            <h1>SONOS</h1>
            <h2>speaks!</h2>
            <p className="landing-introduction">Integrate your SONOS speakers into your<br/>
home automation.</p>
            <p className="landing-introduction">Get notified of events, in high fidelity.</p>
            <img className="speaker-left" src="/static/img/sonos-bubble-left.svg"/>
            <img className="speaker-right" src="/static/img/sonos-bubble-right.svg"/>
            
            <p className="connect-sonos"><button className="sonos connect" onClick={() => { location.href = createSonosAuthUri(sonosApiAppKey, accountid, redirectUriRoot + "/sonos_auth") }}>Connect with SONOS</button></p>
            <GoogleLogout className="google-logout" onLogoutSuccess={responseGoogleLogout}/>
        </div>)
}

function renderLoggedIn(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var accountid = account != null && 'accountid' in account ?  accountid = account['accountid'] : null
    var isGoogleSignedIn = accountid != null
    return (<div className="content">
            <h2>Sonos speaks!</h2>
            {account.sonos.players.length == 0 && <div><p>We have not found any players.</p><p>Go shopping and come back when you bought and installed a new SONOS player ;-)</p></div>}
            {account.sonos.players.length == 1 && <span>We have found 1 player.</span>}
            {account.sonos.players.length > 1 && <span>We have found {account.sonos.players.length} players.</span>}
            <table>
                <tbody>
                    {account.sonos.players.map(player => {
                        return (<SonosPlayerView player={player} key={`player_${player.playerId}`}/>)
                    })}
                </tbody>
            </table>
            <img className="speaker-right corner" src="/static/img/sonos-bubble-right.svg"/>
            <GoogleLogout className="google-logout" onLogoutSuccess={responseGoogleLogout}/>
            <a className="unlink" href="#" onClick={sonosLogout.bind(null, account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)}>unlink this SONOS account</a>
        </div>)
}

function render(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var accountid = account != null && 'accountid' in account ?  accountid = account['accountid'] : null
    var isGoogleSignedIn = accountid != null
    console.log(`render(${account}, ${isSonosSignedIn}, ${sonosApiAppKey}, ${redirectUriRoot})`)
    if (!isGoogleSignedIn)
        return renderLanding()
    else if (isGoogleSignedIn && !isSonosSignedIn)
        return renderLoggedInWithoutSonos(sonosApiAppKey, accountid, redirectUriRoot)
    else if (isGoogleSignedIn && isSonosSignedIn)
        return renderLoggedIn(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
}

renderRoot(null, false)

