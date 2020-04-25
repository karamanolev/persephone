import React from 'react';
import {FormGroup, InputGroup, Switch} from '@blueprintjs/core';
import {FormError} from 'components/FormError.jsx';

const DEFAULT_PROJECT = {
    supersede_same_branch_builds: true,
    auto_archive_no_diff_builds: true,
    auto_approve_master_builds: true,
};

export class ProjectForm extends React.PureComponent {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        let value;

        if (e.target.type === 'checkbox') {
            value = e.target.checked;
        } else {
            value = e.target.value;
        }

        this.props.onChange({
            ...(this.props.project || DEFAULT_PROJECT),
            [e.target.name]: value,
        });
    }

    render() {
        const project = this.props.project || DEFAULT_PROJECT;
        const errors = this.props.errors || {};

        return <React.Fragment>
            <FormGroup
                label="Name"
                labelFor="name"
                helperText="Name for your project - used for display purposes."
            >
                <InputGroup
                    name="name"
                    value={project.name || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.name}/>
            </FormGroup>

            <FormGroup
                label="Public Endpoint"
                labelFor="public_endpoint"
                helperText="An absolute URL to this website - used for constructing URLs to builds."
            >
                <InputGroup
                    id="public_endpoint"
                    name="public_endpoint"
                    value={project.public_endpoint || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.public_endpoint}/>
            </FormGroup>

            <FormGroup
                label="GitHub Repo Name:"
                labelFor="github_repo_name"
                helperText="Owner/Repo of the GitHub project."
            >
                <InputGroup
                    id="github_repo_name"
                    name="github_repo_name"
                    value={project.github_repo_name || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.github_repo_name}/>
            </FormGroup>

            <FormGroup
                label="GitHub API Key:"
                labelFor="github_api_key"
            >
                <InputGroup
                    id="github_api_key"
                    name="github_api_key"
                    value={project.github_api_key || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.github_api_key}/>
            </FormGroup>

            <FormGroup>
                <Switch
                    name="supersede_same_branch_builds"
                    label="Supersede Same Branch Builds"
                    value={project.supersede_same_branch_builds || false}
                    onChange={this.handleChange}
                />
                <FormError error={errors.supersede_same_branch_builds}/>
                <Switch
                    name="auto_archive_no_diff_builds"
                    label="Auto Archive No Diff Builds"
                    value={project.auto_archive_no_diff_builds || false}
                    onChange={this.handleChange}
                />
                <FormError error={errors.auto_archive_no_diff_builds}/>
                <Switch
                    name="auto_approve_master_builds"
                    label="Auto Approve Master Builds"
                    value={project.auto_approve_master_builds || false}
                    onChange={this.handleChange}
                />
                <FormError error={errors.auto_approve_master_builds}/>
            </FormGroup>

            <FormGroup
                label="Max Master Builds To Keep:"
                labelFor="max_master_builds_to_keep"
            >
                <InputGroup
                    id="max_master_builds_to_keep"
                    name="max_master_builds_to_keep"
                    value={project.max_master_builds_to_keep || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.max_master_builds_to_keep}/>
            </FormGroup>

            <FormGroup
                label="Max Branch Builds To Keep:"
                labelFor="max_branch_builds_to_keep"
            >
                <InputGroup
                    id="max_branch_builds_to_keep"
                    name="max_branch_builds_to_keep"
                    value={project.max_branch_builds_to_keep || ''}
                    onChange={this.handleChange}/>
                <FormError error={errors.max_branch_builds_to_keep}/>
            </FormGroup>
        </React.Fragment>;
    }
}
