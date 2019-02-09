import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
import React from 'react';
import ReactDOM from 'react-dom';

function renderRoot(accountid, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    console.log("renderRoot")
   ReactDOM.render(renderLanding(accountid, isSonosSignedIn, sonosApiAppKey, redirectUriRoot), document.getElementById('landing'))
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
    .then(function(json) {
        console.log(json)
        if ("sonos" in json) {
            renderRoot(json['accountid'], true, json['sonosApiAppKey'], json['redirectUriRoot'])
        } else {
            renderRoot(json['accountid'], false, json['sonosApiAppKey'], json['redirectUriRoot'])
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

function renderLanding(accountid, isSonosSignedIn, sonosApiAppKey, redirectUriRoot)
{
    var isGoogleSignedIn = accountid != null
    console.log(`renderLanding(${accountid}, ${isSonosSignedIn}, ${sonosApiAppKey}, ${redirectUriRoot})`)
    return (<div>
            <h1>Sonos Power-Tools</h1>

            <div className="landing">
                <p className="landing-introduction">Let your Sonos speakers talk to you</p>
                <p className="landing-introduction">Simple, three-step setup:</p>

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
                    {!isSonosSignedIn && <li><a href={createSonosAuthUri(sonosApiAppKey, accountid, redirectUriRoot + "/sonos_auth")}>Connect with Sonos</a> to receive an API key</li>}
                    {isSonosSignedIn && <li>Sonos is signed in</li>}
                    <li>HTTP POST the text that you want your speakers to say.</li>
                </ol>
            </div>
        </div>)
}

renderRoot(null, false)

