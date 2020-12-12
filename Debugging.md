# Debug Backchannels

## VSCode

### .NET

1. Follow the [Prerequisites](https://code.visualstudio.com/docs/containers/debug-netcore#_prerequisites) steps from this [VSCode tutorial](https://code.visualstudio.com/docs/containers/debug-netcore).
2. The docker containers need the `$DOCKERHOST` variable, and currently VSCode doesn't offer a way to do this dynamically.
   1. `cp .env.example .env`
   2. Replace `DOCKERHOST` with the output of `./manage dockerhost`, also replace the IP in `LEDGER_URL` with the output.
3. Launch the desired debuggers from the Run view. You can launch multiple debuggers at the same time:
   - .NET Backchannel - Acme
   - .NET Backchannel - Bob
   - .NET Backchannel - Faber
   - .NET Backchannel - Mallory
4. Run the tests using the manage script. The manage script will automatically detect if any of the agents is already running and skip the startup. You must make sure the backchannels that are passed to the `./manage run` script are the same as the backchannels started with the debugger.
   - If you now, for example, run `./manage run -d dotnet -t @T001-AIP10-RFC0160` it will run the tests using the backchannels you started from the debugger.

For more information on debugging in VSCode see [the docs](https://code.visualstudio.com/docs/editor/debugging).

#### Troubleshooting

##### Process 'dotnet dev-certs https --check --trust'

If you get the following error:

```shell
Error: Process 'dotnet dev-certs https --check --trust' exited with code 9
Error:
```

This means the ASP.NET Core development certificate is not quite working. Running the following should fix the problem:

```shell
dotnet dev-certs https --clean
dotnet dev-certs https --trust
```

See: https://github.com/microsoft/vscode-docker/issues/1761
