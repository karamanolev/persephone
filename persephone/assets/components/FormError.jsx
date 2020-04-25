import React from 'react';
import {Icon} from '@blueprintjs/core';

export class FormError extends React.PureComponent {
    render() {
        if (!this.props.error) {
            return null;
        }

        return <div className="form-error">
            <Icon icon="error" size={8}/>{' '}
            {this.props.error}
        </div>;
    }
}
