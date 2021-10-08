-- ioのようなstandard Lua modulesを使う場合は
-- docker run -it -p 8050:8050 scrapinghub/splash --disable-lua-sandbox
-- 上記コマンドでlistenしなければいけない．sandboxをdisableする必要がある．
-- see detail: https://splash.readthedocs.io/en/stable/scripting-tutorial.html#lua-sandbox
function main(splash)
    -- MathJaxを使っている場合にrenderingのためにwaitする関数．

    assert(splash:go(splash.args.url))

    local get_math_jax = splash:jsfunc([[
        function () {
            return window.MathJax;
        }
    ]])

    if get_math_jax() then
        -- MathJaxを使っているサイト
        -- renderingが完了するまでwait
        while not splash:select('math') do
            splash:wait(0.1)
        end
    end

    return splash:html()
end