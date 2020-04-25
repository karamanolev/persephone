import React from 'react';
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';
import {Login} from 'pages/Login.jsx';
import {Dashboard} from 'pages/Dashboard.jsx';
import {ProjectDashboard} from 'pages/ProjectDashboard.jsx';
import {ProjectCreate} from 'pages/ProjectCreate.jsx';
import {BuildDashboard} from 'pages/BuildDashboard.jsx';
import {NavbarWrapper} from 'pages/NavbarWrapper.jsx';
import {ProjectEdit} from 'pages/ProjectEdit.jsx';

export class Root extends React.PureComponent {
    renderNavbarRoutes() {
        return (
            <Switch>
                <Route exact path="/" component={Dashboard}/>
                <Route exact path="/projects/create" component={ProjectCreate}/>
                <Route exact path="/projects/:projectId" component={ProjectDashboard}/>
                <Route exact path="/projects/:projectId/edit" component={ProjectEdit}/>
                <Route exact path="/projects/:projectId/builds/:buildId"
                       component={BuildDashboard}/>
            </Switch>
        );
    }

    render() {
        return (
            <Router>
                <Switch>
                    <Route exact path="/login" render={props => <Login {...props}/>}/>
                    <Route path="" render={props => (
                        <NavbarWrapper>
                            {this.renderNavbarRoutes()}
                        </NavbarWrapper>
                    )}/>
                </Switch>
            </Router>
        );
    }
}
