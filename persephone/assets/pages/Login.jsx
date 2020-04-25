import $ from 'jquery';
import React from 'react';
import {Button, Callout, FormGroup, InputGroup} from '@blueprintjs/core';

import logo from 'img/logo.svg';
import {BuildsAPI} from 'BuildsAPI.js';
import {APIError} from 'APIUtil.js';

export class Login extends React.PureComponent {
    constructor(props) {
        super(props);

        this.state = {
            username: '',
            password: '',
        };
    }

    componentDidMount() {
        $('#root').addClass('root-login');
    }

    componentWillUnmount() {
        $('#root').removeClass('root-login');
    }

    async login() {
        try {
            await BuildsAPI.login(this.state.username, this.state.password);
            this.props.history.push('/');
        } catch (e) {
            if (e instanceof APIError && e.response.status === 403) {
                this.setState({
                    error: 'Invalid username or password.',
                });
            } else {
                throw e;
            }
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        this.login();
    }

    render() {
        return <form className="login-root" onSubmit={e => this.handleSubmit(e)}>
            <div className="logo">
                <img src={logo}/>
            </div>

            <FormGroup label="Username" labelFor="username">
                <InputGroup
                    id="username"
                    placeholder="username"
                    value={this.state.username}
                    onChange={e => this.setState({username: e.target.value})}/>
            </FormGroup>

            <FormGroup label="Password" labelFor="password">
                <InputGroup
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={this.state.password}
                    onChange={e => this.setState({password: e.target.value})}
                />
            </FormGroup>

            {this.state.error ? (
                <Callout intent="danger">
                    {this.state.error}
                </Callout>
            ) : null}

            <Button
                id="submit"
                type="submit"
                intent="primary"
                fill
            >
                Login
            </Button>
        </form>;
    }
}
