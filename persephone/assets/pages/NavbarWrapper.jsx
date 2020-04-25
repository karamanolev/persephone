import React from 'react';
import {Link, Redirect} from 'react-router-dom';
import {Classes, Icon, Menu, MenuDivider, MenuItem} from '@blueprintjs/core';
import logoWhite from 'img/logo-white.svg';
import classNames from 'classnames';
import $ from 'jquery';
import {BuildsAPI} from 'BuildsAPI.js';
import {APIError} from 'APIUtil.js';

class NavMenuItem extends React.PureComponent {
    render() {
        return (
            <Link to={this.props.to}
                  className={classNames(Classes.MENU_ITEM, this.props.className)}>
                <Icon icon={this.props.icon}/>
                <div className="bp3-text-overflow-ellipsis bp3-fill">
                    {this.props.text}
                </div>
            </Link>
        );
    }
}

export class NavbarWrapper extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            projects: [],
        };
    }

    componentDidMount() {
        $('#root').addClass('root-navbar');
        this.fetchData();
    }

    componentWillUnmount() {
        $('#root').removeClass('root-navbar');
    }

    async fetchData() {
        try {
            this.setState({
                projects: await BuildsAPI.getProjects(),
            });
        } catch (e) {
            if (e instanceof APIError && e.response.status === 403) {
                this.setState({
                    redirect: '/login',
                });
            } else {
                throw e;
            }
        }
    }

    async logout() {
        await BuildsAPI.logout();
        this.setState({
            redirect: '/login',
        });
    }

    render() {
        return <React.Fragment>
            {this.state.redirect ? <Redirect to={this.state.redirect}/> : null}
            <div className="navbar bp3-dark">
                <div className="logo">
                    <img src={logoWhite}/>
                </div>
                <Menu>
                    <NavMenuItem to="/" icon="menu" text="Dashboard"/>
                    {this.state.projects.length ? (
                        <React.Fragment>
                            <MenuDivider/>
                            {this.state.projects.map(project => (
                                <NavMenuItem
                                    key={project.id}
                                    to={`/projects/${project.id}`}
                                    icon="database"
                                    text={project.name}
                                />
                            ))}
                        </React.Fragment>
                    ) : null}
                    <MenuDivider/>
                    <MenuItem icon="log-out" text="Exit" onClick={() => this.logout()}/>
                </Menu>
            </div>
            <div className="main-pane">
                {this.props.children}
            </div>
        </React.Fragment>;
    }
}
