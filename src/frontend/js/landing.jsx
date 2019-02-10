import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
import React from 'react';
import ReactDOM from 'react-dom';

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

function sonosPlayTest(apiKey)
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
        body: JSON.stringify({"text": "Test successful", "languagecode": "en-US", "key": apiKey})
    }).then(response => console.log(response))
}

function renderLanding()
{
    return (<div className="landing">
            <h1>SONOS</h1>
            <h2>speaks!</h2>
            <p className="landing-introduction">Integrate your SONOS speakers into your<br/>
home automation.</p>
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
                        return (
                            <tr key={`player_${player.playerId}`}>
                                <td>
                                    <p className="player-name">Player „{player.playerId}”</p>
                                    <p className="api-key-label">Your API key for this player is:</p>
                                    <div>
                                        <span className="api-key">{player.apiKey}</span>
                                        <button className="sonos test-button" onClick={sonosPlayTest.bind(this, player.apiKey)}>Test now</button>
                                    </div>
                                </td>
                            </tr>)
                    })}
                </tbody>
            </table>
            <img className="speaker-right corner" src="/static/img/sonos-bubble-right.svg"/>
            <GoogleLogout className="google-logout" onLogoutSuccess={responseGoogleLogout}/>
            <a className="unlink" href="#" onClick={sonosLogout.bind(null, account, sonosApiAppKey, redirectUriRoot)}>unlink this SONOS account</a>
        </div>)
}

function render(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var accountid = account != null && 'accountid' in account ?  accountid = account['accountid'] : null
    var isGoogleSignedIn = accountid != null
    console.log(`render(${account}, ${isSonosSignedIn}, ${sonosApiAppKey}, ${redirectUriRoot})`)
    return (<div className="root inner">
            <div className="top-bar secondary"/>
            {!isGoogleSignedIn && renderLanding()}
            {isGoogleSignedIn && !isSonosSignedIn && renderLoggedInWithoutSonos(sonosApiAppKey, accountid, redirectUriRoot)}
            {isGoogleSignedIn && isSonosSignedIn && renderLoggedIn(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)}
            <div className="bottom-bar secondary"/>
        </div>)
}

renderRoot(null, false)

