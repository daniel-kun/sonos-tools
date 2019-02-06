import { GoogleLogin } from 'react-google-login';
import { GoogleLogout } from 'react-google-login';
import React from 'react';
import ReactDOM from 'react-dom';

function renderRoot(isGoogleSignedIn, isSonosSignedIn)
{
    console.log("renderRoot")
    ReactDOM.render(renderLanding(isGoogleSignedIn, isSonosSignedIn), document.getElementById('landing'))
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
    }).then(
        response => {
            console.log(response)
            renderRoot(true, false);
        }); // parses response to JSON
}

function responseGoogleFailure(error)
{
    console.log(error);
}

function responseGoogleLogout()
{
    renderRoot(false, false);
}

function renderLanding(isGoogleSignedIn, isSonosSignedIn)
{
    console.log(`renderLanding(${isGoogleSignedIn}, ${isSonosSignedIn})`)
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
                    <li>Connect with Sonos to receive an API key</li>
                    <li>HTTP POST the text that you want your speakers to say.</li>
                </ol>
            </div>
        </div>)
}

renderRoot(false, false)

