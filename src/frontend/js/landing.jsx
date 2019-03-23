import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
import { FakeGoogleLogin } from './fake-google-login.jsx';
import { FakeGoogleLogout } from './fake-google-login.jsx';
import React from 'react';
import ReactDOM from 'react-dom';
import {SonosPlayerView} from './sonosplayerview.js';

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

function fakeResponseGoogleLogin(googleUser)
{
    console.log("fakeResponseGoogleLogin")
    fetch("/receive_google_auth", {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"token": "XXX_GOOGLE_ID_TOKEN"}),
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
    fetch("/logout", {
        method: 'POST',
        cache: 'no-cache',
        credentials: 'include'
    })
    renderRoot(null, false);
}

function createSonosAuthUri(clientId, accountid, redirectUri)
{
    var sonosApiEndpoint = window.sonosToolsSonosApiEndpoint
    var state = window.btoa(JSON.stringify({
                'accountid': accountid
        }))
    return `${sonosApiEndpoint}/login/v3/oauth?client_id=${clientId}&response_type=code&state=${state}&scope=playback-control-all&redirect_uri=${redirectUri}`
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
            
            {!window.sonosToolsIsDevEnv && <GoogleLogin 
                clientId="166334197578-sem3ib4jfiqm8k59npc1s3ddrro5f5bs.apps.googleusercontent.com"
                isSignedIn={true}
                onSuccess={responseGoogleLogin}
                onFailure={responseGoogleFailure}/>}
            {window.sonosToolsIsDevEnv && <FakeGoogleLogin onSuccess={fakeResponseGoogleLogin}/>}
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
            {!window.sonosToolsIsDevEnv && <GoogleLogout className="google-logout" onLogoutSuccess={responseGoogleLogout}/>}
            {window.sonosToolsIsDevEnv && <FakeGoogleLogout onLogoutSuccess={responseGoogleLogout}/>}
        </div>)
}

function renderLoggedIn(account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var accountid = account != null && 'accountid' in account ?  accountid = account['accountid'] : null
    var isGoogleSignedIn = accountid != null
    return (<div className="content">
            <h2>Sonos speaks!</h2>
            {account.sonos.players.length == 0 && <div><p>We have not found any players.</p><p>Go shopping and come back when you bought and installed a new SONOS player ;-)</p></div>}
            {account.sonos.players.length == 1 && <span>We have found 1 player.<br/>Try it out now.</span>}
            {account.sonos.players.length > 1 && <span>We have found {account.sonos.players.length} players.<br/>Try them out now.</span>}
            <SonosPlayerView players={account.sonos.players}/>
            {!window.sonosToolsIsDevEnv && <GoogleLogout className="google-logout" onLogoutSuccess={responseGoogleLogout}/>}
            {window.sonosToolsIsDevEnv && <FakeGoogleLogout onLogoutSuccess={responseGoogleLogout}/>}
            <a className="unlink" href="#" onClick={sonosLogout.bind(null, account, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)}>Unlink this Sonos account</a>
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

window.sonosToolsIsDevEnv = document.getElementById('sonostools-entrypoint').getAttribute('data-sonostools_devenv') == "true"
window.sonosToolsSonosApiEndpoint = document.getElementById('sonostools-entrypoint').getAttribute('data-sonostools_sonos_api_endpoint')

fetch("/check_auth", {
    credentials: 'include',
    cache: 'no-cache'
})
    .then(response => {
        console.log(response)
        if (response.status == 200) {
            response.json().then(account => {
                renderRoot(account, "sonos" in account, account["sonosApiAppKey"], account["redirectUriRoot"])
            }).catch(err => {
                console.log('check_auth - catched when parsing json-response')
                console.log(err)
                renderRoot(null, false)
            })
        } else {
            console.log(`check_auth - non-200 status code: ${response.status}`)
            renderRoot(null, false)
        }
    })
    .catch(err => {
        console.log('check_auth - catched when fetching request')
        console.log(err)
        renderRoot(null, false)
    })

