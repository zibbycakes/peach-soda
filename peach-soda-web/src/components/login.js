import React, {useState} from 'react';
import { Button, Input } from '@material-ui/core';
import { login } from '../config/endpoints';


function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    return (
        <div>
            <h1>Please log in</h1>
            <form className="login-form">
                <Input type="text" onChange={e => setUsername(e.target.value)} placeholder="Username" />
                <Input type="text" onChange={e => setPassword(e.target.value)} placeholder="Password" />
                <Button onClick={e=>{apiLogin(username, password)}}>Log in</Button>
            </form>
        </div>
    );
}

function apiLogin() {
    window.fetch(login(), {method: 'POST'})
      .then(res => res.json())
      .then((result)=> {
        //upstream set auth to true
        console.log(result)
      })
}

export default Login;
