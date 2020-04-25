import React from 'react';
import {CardGrid} from 'ui/CardGrid.jsx';
import {Redirect} from 'react-router-dom';
import {Card} from 'ui/Card.jsx';
import {Button, Toaster} from '@blueprintjs/core';
import {ProjectForm} from 'components/ProjectForm.jsx';
import {BuildsAPI} from 'BuildsAPI.js';
import {APIError} from 'APIUtil.js';

export class ProjectCreate extends React.PureComponent {
    constructor(props) {
        super(props);

        this.state = {
            project: null,
        };
    }

    handleChange(p) {
        this.setState({
            project: p,
        });
    }

    async handleSubmit(e) {
        e.preventDefault();

        try {
            const project = await BuildsAPI.createProject(this.state.project);
            this.setState({
                redirect: `/projects/${project.id}`,
            });
        } catch (ex) {
            if (ex instanceof APIError && ex.response.status === 400) {
                this.setState({
                    errors: ex.responseJSON,
                });
            }
        }
    }

    render() {
        return (
            <CardGrid>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                <Card>
                    <h1>Create Project</h1>
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
                            Create Project
                        </Button>
                    </form>
                </Card>
            </CardGrid>
        );
    }
}
