customElements.define('float-input',
    class extends HTMLElement {
        connectedCallback() {
            let field;

            if (this.type === 'text' && this.multiline) {
                field = `<textarea class="field__input" name="${this.id}" type="${this.type}"
                          placeholder="${this.label}" ${this.extra}></textarea>`;
            } else if (this.type === 'select') {
                field = `<select class="field__input" name="${this.id}" ${this.extra}>
                    <option value="">${this.label}</option>
                    ${this.innerHTML}
                </select>`;
            } else {
                // A regular input, with the field determined by the type attribute
                field = `<input class="field__input" name="${this.id}" type="${this.type}"
                       placeholder="${this.label}" ${this.extra}>`;
            }
        
            const template = `
                <div class="field" ${this.container_extra}>
                    ${field}
                    <label class="field__label" for="${this.id}">${this.label}</label>
                </div>
            `;
            this.innerHTML = template;

            /* Initialize Properties */
            this.input_node = this.querySelector(`[name="${this.id}"]`);

            // Setup events and callbacks
            // Input Masking
            if(this.input_mask_name){
                window.addEventListener('load', ()=>{
                    if(typeof this.input_node.pants_data === "undefined"){
                        this.input_node.pants_data = {};
                    }
                    this.input_mask = IMask(this.input_node, this.named_masks[this.input_mask_name]);
                })
            }

            // Select elements publicizing what value is currently selected
            if(this.type === "select"){
                // Select elements need to know what the current option is in order to style "nothing chosen"
                this.input_node.dataset.picked_option = "";
                this.input_node.addEventListener('change', function(){
                    // 'this' is the select element
                    this.dataset.picked_option = this.value;
                })
            }

            // Setup Tagify Autocomplete
            if (this.type === 'autocomplete' && this.multiline) {
                // Setup combobox for selecting/specifying ingredient/recipe/one off food
                function tagTemplate(component) {
                    return `
                        <tag title="${component.url}"
                                contenteditable='false'
                                spellcheck='false'
                                tabIndex="-1"
                                class="tagify__tag"
                                ${this.getAttributes(component)}>
                            <x title='' class='tagify__tag__removeBtn' role='button' aria-label='remove tag'></x>
                            <div>
                                <i class='fas fa-${component.component_type === 'recipe' ? 'hamburger' : 'carrot'}'></i>
                                <span class='tagify__tag-text'>${component.name}</span>
                            </div>
                        </tag>
                    `
                }

                function suggestionItemTemplate(component) {
                    return `
                        <div ${this.getAttributes(component)}
                            class='tagify__dropdown__item'
                            tabindex="0"
                            role="option">
                            <i class='fas fa-${component.component_type === 'recipe' ? 'hamburger' : 'carrot'}'></i>
                            <strong>${component.name}</strong>
                        </div>
                    `
                }

                let tagify = new Tagify(this.input_node, {
                    maxTags: 1,
                    whitelist: [],
                    templates: {
                        tag: tagTemplate,
                        dropdownItem: suggestionItemTemplate,
                        dropdownItemNoMatch: function (data) {
                            return `No match. Create one time entry for: ${data.value}`
                        }
                    },
                    dropdown: {
                        enabled: 1,
                        searchKeys: ['name']
                    }
                })
                //let controller; // for aborting the call TODO implement arbortability
                // listen to any keystrokes which modify tagify's input
                tagify.on('input', onInput);

                function onInput(e) {
                    var value = e.detail.value;
                    tagify.settings.whitelist.length = 0; // reset the whitelist

                    // https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort
                    //controller && controller.abort();
                    //controller = new AbortController();

                    // show loading animation and hide the suggestions dropdown
                    tagify.loading(true).dropdown.hide.call(tagify);

                    pants.search_components(value)
                        .then(function (response) {
                            let results = response.results.map(component => {
                                // Give each recipe a 'value' that Tagify will use and the API will understand
                                component['value'] = component['name'];
                                // Give each component a component_type that we can use to differentiate between ingredients and recipes
                                component['component_type'] = component.url.split('/').splice(-3)[0];
                                return component
                            })
                            // update whitelist Array in-place
                            tagify.settings.whitelist.splice(0, results.length, ...results)
                            tagify.loading(false).dropdown.show.call(tagify, value); // render the suggestions dropdown
                        })
                }
            } else if(this.type === 'autocomplete'){
                // Setup regular autocomplete
                this.autocomplete = new autoComplete({
                    selector: ".field__input[type='autocomplete']",
                    data: {
                        src: ['some', 'results', 'results', 'results', 'resultsrdsadjklsahfdjklsafhdjkslafhdjksla'],
                        cache: false
                    },
                    highlight: true,
                    resultsList: {
                        render: true,
                        position: "beforebegin"
                    },
                    onSelection: feedback=>{
                        this.input_node.blur();
                        this.input_node.value = feedback.selection.value;
                    },
                })
            }

        }

        /* Input Mask */
        named_masks = {
            // Mask that ensures only 6 total digits, max 3 decimals
            'nutrition_mask': {mask: /^(?=^[\d.]{0,7}$)\d{0,6}(\.\d{0,3})?$/},
            // Mask that ensures only lowercase letters, numbers and dashes
            "slug_mask": {mask: /^[0-9a-z-]*$/},
            // Ensures only lowercase letters, numbers, dashes, and commas
            "tag_mask": {mask: /^[0-9a-z,-]*$/}
        }
        // The actual input mask created by IMask
        input_mask = undefined;

        /* Properties */

        input_node = undefined;

        /* Methods */

        /**
         * Add an option if the input type is a select
         * @param value {string} the value of the new option
         * @param text {string} the text of the new option
         */
        addOption(value, text){
            if(this.type === 'select'){
                let new_option = document.createElement('option');
                new_option.value = value;
                new_option.innerText = text;
                this.input_node.appendChild(new_option)
            }
        }

        /* Attributes */

        // Determines what name the input should have
        get name() {
            return this.getAttribute("name") || "";
        }
        set name(value) {
            return this.setAttribute("name", value)
        }

        // What type of input to create
        get type() {
            return this.getAttribute("type") || "text";
        }
        set type(value) {
            return this.setAttribute("type", value)
        }

        // If we expect multiline input
        get multiline() {
            return this.hasAttribute("multiline");
        }
        set multiline(value) {
            return this.setAttribute("multiline", value)
        }

        // What the floating label should say
        get label() {
            return this.getAttribute("label")
        }
        set label(value) {
            return this.setAttribute("label", value)
        }

        // An extra string to place in the attributes of the template input element
        get extra() {
            return this.getAttribute("extra") || "";
        }
        set extra(value) {
            return this.setAttribute("extra", value)
        }

        // An extra string to place in the attributes of the template wrapper element
        get container_extra() {
            return this.getAttribute("container_extra") || "";
        }
        set container_extra(value) {
            return this.setAttribute("container_extra", value)
        }

        // input mask is for js input masking options with IMask library.
        // Should be the name of a named mask in this element
        // TODO make it so that you can specify your own mask?
        get input_mask_name() {
            return this.getAttribute("input_mask_name");
        }
        set input_mask_name(value) {
            return this.setAttribute("input_mask_name", value)
        }

        // TODO hint
        // hint is a paragraph explaining what could be put in, or limitations to inputs. Possibly should be made visible on focus

        /* Replacements for Input properties */
        get value(){
            return this.input_node.value;
        }
        set value(value){
            this.input_node.value = value;
            // If this has an input mask, the mask's internal value will need to be synchronized.
            if(this.input_mask){
                this.input_mask.updateValue();
            }

            if(this.type === "select"){
                // Need to trigger a change so that the data-picked_option updates
                let evt = document.createEvent("HTMLEvents");
                evt.initEvent("change", false, true);
                this.input_node.dispatchEvent(evt);
            }
        }

        get valueAsDate(){
            return this.input_node.valueAsDate;
        }
        set valueAsDate(value){
            return this.input_node.valueAsDate = value;
        }

        get id(){
            return this.getAttribute("id");
        }
        set id(value){
            return this.setAttribute("id", value);
        }

        get autocompleteSrc(){
            return this.getAttribute("autocompleteSrc");
        }
        set autocompleteSrc(value){
            this.autocomplete.data.src = value;
            return this.setAttribute("autocompleteSrc", value);
        }


    }
);