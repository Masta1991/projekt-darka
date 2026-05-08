import streamlit as st
import time
import streamlit.components.v1 as components

st.write("Current time:", time.time())
val = st.text_input("test_input", key="my_input")
st.write("Value is:", val)

js_code = """
<script>
const parentDoc = window.parent.document;
window.testBlur = function() {
    const input = parentDoc.querySelector('input[aria-label="test_input"]');
    input.focus();
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    nativeInputValueSetter.call(input, "hello " + Date.now());
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.blur();
}
window.testEnter = function() {
    const input = parentDoc.querySelector('input[aria-label="test_input"]');
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    nativeInputValueSetter.call(input, "world " + Date.now());
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
}
window.testForm = function() {
    const input = parentDoc.querySelector('input[aria-label="test_input"]');
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
    nativeInputValueSetter.call(input, "form " + Date.now());
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.form.requestSubmit();
}
</script>
"""
components.html(js_code, height=0)
