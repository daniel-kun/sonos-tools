import React from 'react';

export function FakeGoogleLogin(props) {
    return <button onClick={props.onSuccess}>Fake Google Login</button>
}

export function FakeGoogleLogout(props) {
    return <button onClick={props.onLogoutSuccess}>Fake Google Logout</button>
}

