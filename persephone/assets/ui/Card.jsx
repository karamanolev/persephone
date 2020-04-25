import React from 'react';
import classNames from 'classnames';

export class Card extends React.PureComponent {
    renderLink() {

    }

    render() {
        return (
            <div
                className={classNames('card', this.props.className, {
                    clickable: this.props.onClick,
                })}
                onClick={this.props.onClick}
            >
                {this.props.children}
            </div>
        );
    }
}
