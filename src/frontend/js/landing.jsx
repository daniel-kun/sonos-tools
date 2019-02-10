import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
import React from 'react';
import ReactDOM from 'react-dom';

function renderRoot(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    console.log("renderRoot")
   ReactDOM.render(renderLanding(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot), document.getElementById('landing'))
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

function renderLanding(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var accountid = account != null && 'accountid' in account ?  accountid = account['accountid'] : null
    var isGoogleSignedIn = accountid != null
    console.log(`renderLanding(${account}, ${isSonosSignedIn}, ${sonosApiAppKey}, ${redirectUriRoot})`)
    return (<div>
            <div className="top-bar secondary"/>
            <div className="landing">
                <h1>SONOS</h1>
                <h2>speaks!</h2>
                <p className="landing-introduction">Integrate your SONOS speakers into your<br/>
home automation.</p>
                <p className="landing-introduction">Get notified of events, in high fidelity.</p>
                <img class="speaker-left" src="/static/img/sonos-bubble-left.svg"/>
                <img class="speaker-right" src="/static/img/sonos-bubble-right.svg"/>
                
                {/*
                <GoogleLogin 
                    clientId="166334197578-sem3ib4jfiqm8k59npc1s3ddrro5f5bs.apps.googleusercontent.com"
                    isSignedIn={true}
                    onSuccess={responseGoogleLogin}
                    onFailure={responseGoogleFailure}/>
                    */}
            </div>
            <div className="section-two secondary">
                <ol>
                    <li>
                    {!isGoogleSignedIn && 
                        <GoogleLogin 
                            clientId="166334197578-sem3ib4jfiqm8k59npc1s3ddrro5f5bs.apps.googleusercontent.com"
                            isSignedIn={true}
                            onSuccess={responseGoogleLogin}
                            onFailure={responseGoogleFailure}/>}
                    {isGoogleSignedIn && <GoogleLogout onLogoutSuccess={responseGoogleLogout}/>}
                    </li>
                    {!isGoogleSignedIn && !isSonosSignedIn && <li>Connect with Sonos to receive an API key</li>}
                    {isGoogleSignedIn && !isSonosSignedIn && <li><a href={createSonosAuthUri(sonosApiAppKey, accountid, redirectUriRoot + "/sonos_auth")}>Connect with Sonos</a> to receive an API key</li>}
                    {isGoogleSignedIn && isSonosSignedIn && <li>Sonos is signed in (<a href='#' onClick={sonosLogout.bind(null, account, sonosApiAppKey, redirectUriRoot)}>log out</a>)</li>}
                    <li>HTTP POST the text that you want your speakers to say.</li>
                </ol>

                {account != null && 'sonos' in account && 'players' in account.sonos &&
                    <table>
                        <tbody>
                            {account.sonos.players.map(player => {
                                return (
                                    <tr key={`player_${player.playerId}`}>
                                        <td>
                                            <p>Name: {player.playerId}</p>
                                            <p>API Key: {player.apiKey}</p>
                                        </td>
                                        <td>
                                            <a href='#' onClick={sonosPlayTest.bind(this, player.apiKey)}>Test now</a>
                                        </td>
                                    </tr>)
                            })}
                        </tbody>
                    </table>}
            </div>
        </div>)
}

renderRoot(null, false)

