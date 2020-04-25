import React from 'react';
import classNames from 'classnames';

export class CardGrid extends React.PureComponent {
    render() {
        return (
            <div className="card-grid">
                {this.props.children}
            </div>
        );
    }
}
