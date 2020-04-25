import React from 'react';
import {Icon} from '@blueprintjs/core';
import $ from 'jquery';
import {CardGrid} from 'ui/CardGrid.jsx';
import {Redirect} from 'react-router-dom';
import {Card} from 'ui/Card.jsx';
import {BuildsAPI} from 'BuildsAPI.js';

export class Dashboard extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            projects: [],
        };
    }

    componentDidMount() {
        this.fetchData();
    }

    async fetchData() {
        this.setState({
            projects: await BuildsAPI.getProjects(),
        });
    }

    goToProject(project) {
        this.setState({redirect: `/projects/${project.id}`});
    }

    createProject() {
        this.setState({redirect: '/projects/create'});
    }

    render() {
        return (
            <CardGrid>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                {this.state.projects.map(project => (
                    <Card
                        key={project.id}
                        className="project"
                        onClick={() => this.goToProject(project)}
                    >
                        <h1>{project.name}</h1>

                        {project.github_repo_name}
                    </Card>
                ))}
                <Card className="project new" onClick={() => this.createProject()}>
                    <h1>Create Project</h1>
                    <Icon icon="plus" iconSize={60}/>
                </Card>
            </CardGrid>
        );
    }
}
