# Debug Backchannels

## VSCode

### dotnet

1. Follow the [Prerequisites](https://code.visualstudio.com/docs/containers/debug-netcore#_prerequisites) steps from this [VSCode tutorial](https://code.visualstudio.com/docs/containers/debug-netcore).
1. Set the `${DOCKERHOST}` variable in `tasks.json`. Theoretically VSCode allows to run commands to resolve variables at runtime, however this does not seem to work at the moment. You can retrieve the docker host by running `./manage dockerhost`.
1. Launch the "Docker .NET Core Launch" debugger from the Run view
1. Enjoy. You can now debug and set breakpoints
