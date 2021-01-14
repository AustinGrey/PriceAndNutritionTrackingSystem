<!--
The typical button used on the site. Has props to allow changing between what type of button is primary
-->
<template>
    <button
            :id="id"
            :class="[
                $options.name,
                {primary: primary},
                {'text-only': linkAppearance},
                {'no-wrap': !wraps}
                ]"
            :disabled="disabled"
            :type="type"
    >
        <slot></slot>
    </button>
</template>

<script>
    export default {
        name: "site-button",
        props: {
            id: String,
            primary: {type: Boolean, default: false},
            onClick: Function,
            disabled: {type: Boolean, default: false},
            type: {type: String, default: "button"},
            // If this button should look like a link instead of a button
            linkAppearance: {type: Boolean, default: false},
            wraps: {type: Boolean, default: true}
        }
    }
</script>

<style scoped lang="scss">
    @import 'src/assets/css/_colors.scss';

    button {
        border-radius: var(--border-radius);

        &.no-wrap{
            // Keep everything on one line
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        padding: var(--padding-thin);

        background: c(button, background);
        border: 1px solid c(button, border);
        color: c(button, font);

        &:hover, &:active{
            background: c(button-hover, background);
            border-color: c(button-hover, border);
            color: c(button-hover, font);
        }
        // Defined AFTER hover/active as hover/active should not show any change for disabled buttons
        &[disabled]{
            background: c(button-disabled, background);
            border-color: c(button-disabled, border);
            color: c(button-disabled, font);
        }

        &.primary{
            background: c(button-primary, background);
            border-color: c(button-primary, border);
            color: c(button-primary, font);

            &:hover, &:active{
                background: c(button-primary-hover, background);
                border-color: c(button-primary-hover, border);
                color: c(button-primary-hover, font);
            }

            // Why would a button be both primary, and disabled?
            &[disabled]{
                background: c(button-primary-disabled, background);
                border-color: c(button-primary-disabled, border);
                color: c(button-primary-disabled, font);
            }
        }

        &.text-only {
            border: none;
            padding: 0;
            color: c(button-text-only, font);
            background: none;
            appearance: none;
            text-align: left;

            &:hover {
                color: c(button-text-only-hover, font);
            }
        }
    }
</style>