import React from 'react';
import {Button, Classes, Intent, Popover} from '@blueprintjs/core';

export class YesNoConfirm extends React.PureComponent {
    getPopoverContent() {
        return (
            <div>
                <h3>Confirm deletion</h3>
                <p>
                    {this.props.warning}
                </p>
                <div style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    marginTop: 15,
                }}>
                    <Button
                        className={Classes.POPOVER_DISMISS}
                        style={{marginRight: 10}}
                    >
                        Cancel
                    </Button>
                    <Button
                        intent={Intent.DANGER}
                        className={Classes.POPOVER_DISMISS}
                        onClick={() => this.props.onConfirm()}
                    >
                        Delete
                    </Button>
                </div>
            </div>
        );
    }

    render() {
        return (
            <Popover
                position="auto"
                usePortal={true}
                portalContainer={document.body}
                popoverClassName={Classes.POPOVER_CONTENT_SIZING}
            >
                {this.props.children}
                {this.getPopoverContent()}
            </Popover>
        );
    }
}
