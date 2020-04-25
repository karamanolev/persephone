import React from 'react';
import {Redirect} from 'react-router-dom';
import {Button, ButtonGroup} from '@blueprintjs/core';
import {Card} from 'ui/Card.jsx';
import {CardGrid} from 'ui/CardGrid.jsx';
import {StopPropagation} from 'ui/StopPropagation.jsx';
import {YesNoConfirm} from 'ui/YesNoConfirm.jsx';
import {BuildsAPI} from 'BuildsAPI.js';

class BuildRow extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {};
    }

    goToBuild() {
        this.setState({
            redirect: `/projects/${this.props.projectId}/builds/${this.props.build.id}`,
        });
    }

    render() {
        const build = this.props.build;

        return (
            <tr key={build.id} onClick={() => this.goToBuild(build)}>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                <td>{build.id} (CI #{build.original_build_number})</td>
                <td>{build.state_display}</td>
                <td>{build.branch_name} {build.commit_hash}</td>
                <td>
                    <StopPropagation>
                        <YesNoConfirm
                            onConfirm={() => this.props.onDeleteBuild()}
                            warning={<span>
                                Are you sure you want to delete this build?
                                <br/>
                                You won't be able to recover it.
                            </span>}
                        >
                            <Button icon="trash"/>
                        </YesNoConfirm>
                    </StopPropagation>
                </td>
            </tr>
        );
    }
}

export class ProjectDashboard extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            builds: [],
        };
    }

    componentDidMount() {
        this.fetchBuilds();
    }

    async fetchBuilds() {
        const projectId = this.props.match.params.projectId;

        this.setState({
            project: await BuildsAPI.getProject(projectId),
            builds: await BuildsAPI.getProjectBuilds(projectId),
        });
    }

    async deleteBuild(build) {
        await BuildsAPI.deleteProjectBuild(this.state.project.id, build.id);
        await this.fetchBuilds();
    }

    async deleteProject() {
        await BuildsAPI.deleteProject(this.state.project.id);
        this.setState({
            redirect: '/',
        });
    }

    editProject() {
        this.setState({
            redirect: `/projects/${this.state.project.id}/edit`,
        });
    }

    render() {
        if (!this.state.project) {
            return null;
        }

        return (
            <CardGrid>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                <Card>
                    <h1>
                        {this.state.project.name} ({this.state.project.github_repo_name})
                        {' '}
                        <ButtonGroup large>
                            <Button icon="edit" onClick={() => this.editProject()}/>
                            <YesNoConfirm
                                onConfirm={() => this.deleteProject()}
                                warning={<span>
                                    Are you sure you want to delete this project?
                                    <br/>
                                    You won't be able to recover it.
                                </span>}
                            >
                                <Button icon="trash"/>
                            </YesNoConfirm>
                        </ButtonGroup>
                    </h1>
                </Card>
                <Card>
                    <h2>Builds</h2>

                    <table className="builds-table">
                        <colgroup>
                            <col/>
                            <col/>
                            <col/>
                            <col width="1"/>
                        </colgroup>
                        <tbody>
                            {this.state.builds.map(build => (
                                <BuildRow
                                    key={build.id}
                                    projectId={this.state.project.id}
                                    build={build}
                                    onDeleteBuild={() => this.deleteBuild(build)}
                                />
                            ))}
                        </tbody>
                    </table>
                </Card>
            </CardGrid>
        );
    }
}
