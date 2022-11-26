-- ioのようなstandard Lua modulesを使う場合は
-- docker run -it -p 8050:8050 scrapinghub/splash --disable-lua-sandbox
-- 上記コマンドでlistenしなければいけない．sandboxをdisableする必要がある．
-- see detail: https://splash.readthedocs.io/en/stable/scripting-tutorial.html#lua-sandbox

-- this file is executed at the splash server.

function read_all(file)
    local f = assert(io.open(file, "r"))
    local content = f:read("*all")
    f:close()
    return content
end

-- MathJaxを使っている場合にrenderingのためにwaitする関数．
function main(splash, args)

    splash.resource_timeout = 20.0

    -- Insert MathJax code into the page
    -- after the page is loaded but before the page is rendered.
    -- detail: https://splash.readthedocs.io/en/latest/api.html#executing-custom-javascript-code-within-page-context
    local source = read_all("/code/headless_browser/set-mathjax.js")
    assert(type(source) == "string")

    -- Splash 1.8+ is required to handle POST requests; 
    -- in earlier Splash versions 'http_method' and 'body' arguments are ignored. 
    -- If you work with /execute endpoint and want to support POST requests
    -- you have to handle http_method and body arguments in your Lua script manually.
    assert(splash:go{
        url=splash.args.url,
        http_method="POST",
    }, 'cannot access the URL')

    -- JS function is added to the global scope.
    -- assert(splash:runjs(source))

    while not splash:select('math') do
        splash:wait(0.1)
    end

    -- if splash:evaljs("load_mathjax()") then
    --     -- if the website uses MathJax,
    --     -- splash waits until the rendering finishes.
    --     while not splash:select('math') do
    --         splash:wait(0.1)
    --     end
    -- end

    return splash:html()
end