import React from 'react';
import {CardGrid} from 'ui/CardGrid.jsx';
import {Redirect} from 'react-router-dom';
import {Card} from 'ui/Card.jsx';
import {Button} from '@blueprintjs/core';
import {ProjectForm} from 'components/ProjectForm.jsx';
import {BuildsAPI} from 'BuildsAPI.js';
import {APIError} from 'APIUtil.js';

export class ProjectEdit extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            project: null,
        };
    }

    componentDidMount() {
        this.fetchData();
    }

    async fetchData() {
        const projectId = this.props.match.params.projectId;

        this.setState({
            project: await BuildsAPI.getProject(projectId),
            builds: await BuildsAPI.getProjectBuilds(projectId),
        });
    }

    handleChange(p) {
        this.setState({
            project: p,
        });
    }

    async handleSubmit(e) {
        e.preventDefault();

        try {
            await BuildsAPI.updateProject(this.state.project);
        } catch (ex) {
            if (ex instanceof APIError && ex.response.status === 400) {
                this.setState({
                    errors: ex.responseJSON,
                });
            }
        }
    }

    render() {
        if (this.state.project == null) {
            return null;
        }

        return (
            <CardGrid>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                <Card>
                    <h1>Edit Project {this.state.project.name}</h1>
                </Card>
                <Card>
                    <form className="form-wrapper" onSubmit={e => this.handleSubmit(e)}>
                        <ProjectForm
                            project={this.state.project}
                            errors={this.state.errors}
                            onChange={p => this.handleChange(p)}
                        />
                        <Button
                            id="submit"
                            type="submit"
                            intent="primary"
                        >
                            Save Changes
                        </Button>
                    </form>
                </Card>
            </CardGrid>
        );
    }
}
