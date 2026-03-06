/**
 * Ad Symbiont Amazon Ad Block
 *
 * @package Ad_Symbiont
 */

import { registerBlockType } from '@wordpress/blocks';
import { 
    TextControl, 
    SelectControl, 
    ToggleControl,
    PanelBody,
    PanelRow
} from '@wordpress/components';
import { 
    InspectorControls,
    useBlockProps
} from '@wordpress/block-editor';
import { __ } from '@wordpress/i18n';

registerBlockType( 'ad-symbiont/amazon-ad', {
    title: __( 'Amazon Ad', 'ad-symbiont' ),
    description: __( 'Display an Amazon product ad using ASIN', 'ad-symbiont' ),
    category: 'widgets',
    icon: 'shopping-cart',
    keywords: [ __( 'amazon', 'ad-symbiont' ), __( 'affiliate', 'ad-symbiont' ), __( 'ad', 'ad-symbiont' ) ],
    
    attributes: {
        asin: {
            type: 'string',
            default: '',
        },
        displayMode: {
            type: 'string',
            default: 'append',
        },
        showImage: {
            type: 'boolean',
            default: true,
        },
        showPrice: {
            type: 'boolean',
            default: true,
        },
    },
    
    edit: ( { attributes, setAttributes } ) => {
        const blockProps = useBlockProps();
        
        return (
            <div { ...blockProps }>
                <InspectorControls>
                    <PanelBody title={ __( 'Amazon Ad Settings', 'ad-symbiont' ) } initialOpen={ true }>
                        <PanelRow>
                            <TextControl
                                label={ __( 'ASIN', 'ad-symbiont' ) }
                                value={ attributes.asin }
                                onChange={ ( value ) => setAttributes( { asin: value.toUpperCase() } ) }
                                placeholder={ __( 'e.g., B08N5WRWNW', 'ad-symbiont' ) }
                                help={ __( 'Enter the 10-character Amazon ASIN', 'ad-symbiont' ) }
                            />
                        </PanelRow>
                        <PanelRow>
                            <SelectControl
                                label={ __( 'Display Mode', 'ad-symbiont' ) }
                                value={ attributes.displayMode }
                                options={ [
                                    { label: __( 'Append below link', 'ad-symbiont' ), value: 'append' },
                                    { label: __( 'Replace with ad', 'ad-symbiont' ), value: 'replace' },
                                ] }
                                onChange={ ( value ) => setAttributes( { displayMode: value } ) }
                            />
                        </PanelRow>
                        <PanelRow>
                            <ToggleControl
                                label={ __( 'Show Product Image', 'ad-symbiont' ) }
                                checked={ attributes.showImage }
                                onChange={ ( value ) => setAttributes( { showImage: value } ) }
                            />
                        </PanelRow>
                        <PanelRow>
                            <ToggleControl
                                label={ __( 'Show Price', 'ad-symbiont' ) }
                                checked={ attributes.showPrice }
                                onChange={ ( value ) => setAttributes( { showPrice: value } ) }
                            />
                        </PanelRow>
                    </PanelBody>
                </InspectorControls>
                
                <div className="ad-symbiont-block-placeholder">
                    { attributes.asin ? (
                        <div className="ad-symbiont-preview">
                            <div className="ad-symbiont-preview-icon">🛒</div>
                            <p>
                                <strong>Amazon Product Ad</strong>
                            </p>
                            <p className="ad-symbiont-asin">ASIN: { attributes.asin }</p>
                        </div>
                    ) : (
                        <div className="ad-symbiont-placeholder-text">
                            <p><strong>{ __( 'Amazon Ad', 'ad-symbiont' ) }</strong></p>
                            <p>{ __( 'Enter an ASIN to display an Amazon product ad', 'ad-symbiont' ) }</p>
                        </div>
                    ) }
                </div>
            </div>
        );
    },
    
    save: () => {
        // Dynamic block - render callback handles output.
        return null;
    },
} );
