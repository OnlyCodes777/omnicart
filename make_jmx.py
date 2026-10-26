"""Regenerates OmniCart_TestPlan.jmx. Usage: python make_jmx.py"""
def sampler(name, method, path, code="200", contains=None, body=None):
    args = ('<elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments">'
            + (f'<elementProp name="" elementType="HTTPArgument"><boolProp name="HTTPArgument.always_encode">false</boolProp><stringProp name="Argument.value">{body}</stringProp><stringProp name="Argument.metadata">=</stringProp></elementProp>' if body else '')
            + '</collectionProp></elementProp>')
    def assertion(field, typ, text, n):
        return (f'<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="{n}" enabled="true"><collectionProp name="Asserion.test_strings"><stringProp name="1">{text}</stringProp></collectionProp>'
                f'<stringProp name="Assertion.test_field">{field}</stringProp><intProp name="Assertion.test_type">{typ}</intProp></ResponseAssertion><hashTree/>')
    a = assertion("Assertion.response_code", 8, code, f"Status is {code}")
    if contains: a += assertion("Assertion.response_data", 2, contains, f"Body contains {contains}")
    return (f'<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{name}" enabled="true">{args}'
            f'<stringProp name="HTTPSampler.path">{path}</stringProp><stringProp name="HTTPSampler.method">{method}</stringProp>'
            f'<boolProp name="HTTPSampler.postBodyRaw">{"true" if body else "false"}</boolProp></HTTPSamplerProxy><hashTree>{a}</hashTree>')

body = '{&quot;customer&quot;:&quot;Load Tester&quot;,&quot;email&quot;:&quot;load@example.com&quot;,&quot;total&quot;:99.5}'
bad = '{&quot;customer&quot;:&quot;&quot;,&quot;email&quot;:&quot;nope&quot;,&quot;total&quot;:-5}'
samplers = "".join([
    sampler("GET dashboard page", "GET", "/index.html", contains="OmniCart"),
    sampler("GET health", "GET", "/api/health", contains="ok"),
    sampler("GET products", "GET", "/api/products", contains="Backpack"),
    sampler("GET model metrics", "GET", "/api/model", contains="slope"),
    sampler("GET forecast week 25", "GET", "/api/forecast?week=25", contains="predicted_sales"),
    sampler("GET forecast invalid week (expects 400)", "GET", "/api/forecast?week=abc", code="400"),
    sampler("POST create order", "POST", "/api/orders", code="201", contains="Processing", body=body),
    sampler("POST invalid order (expects 400)", "POST", "/api/orders", code="400", body=bad),
])
listener = lambda g, n: f'<ResultCollector guiclass="{g}" testclass="ResultCollector" testname="{n}" enabled="true"><boolProp name="ResultCollector.error_logging">false</boolProp><stringProp name="filename"></stringProp></ResultCollector><hashTree/>'
xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3"><hashTree>
<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="OmniCart Test Plan" enabled="true"><boolProp name="TestPlan.functional_mode">false</boolProp><boolProp name="TestPlan.serialize_threadgroups">false</boolProp></TestPlan><hashTree>
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Users" enabled="true"><stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
<elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" enabled="true"><boolProp name="LoopController.continue_forever">false</boolProp><stringProp name="LoopController.loops">5</stringProp></elementProp>
<stringProp name="ThreadGroup.num_threads">20</stringProp><stringProp name="ThreadGroup.ramp_time">10</stringProp></ThreadGroup><hashTree>
<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Defaults" enabled="true"><elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments"/></elementProp><stringProp name="HTTPSampler.domain">localhost</stringProp><stringProp name="HTTPSampler.port">8000</stringProp><stringProp name="HTTPSampler.protocol">http</stringProp></ConfigTestElement><hashTree/>
<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="JSON header" enabled="true"><collectionProp name="HeaderManager.headers"><elementProp name="" elementType="Header"><stringProp name="Header.name">Content-Type</stringProp><stringProp name="Header.value">application/json</stringProp></elementProp></collectionProp></HeaderManager><hashTree/>
{samplers}{listener("SummaryReport","Summary Report")}{listener("StatVisualizer","Aggregate Report")}{listener("ViewResultsFullVisualizer","View Results Tree")}
</hashTree></hashTree></hashTree></jmeterTestPlan>'''
open("OmniCart_TestPlan.jmx", "w", encoding="utf-8").write(xml)
