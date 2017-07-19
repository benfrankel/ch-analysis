from django.shortcuts import render

from . import stat


generate_dict = {
    'summary': stat.player_summary,
    'contribution-player-ladder': stat.contribution_player_ladder,
    'contribution-guild-ladder': stat.contribution_guild_ladder,
    'net-win-player-ladder': stat.net_win_player_ladder,
    'net-win-guild-ladder': stat.net_win_guild_ladder,
}


generate_options = (
    'Summary',
    'Contribution player ladder',
    'Contribution guild ladder',
    'Net win player ladder',
    'Net win guild ladder',
)


def index(request):
    context = {'generate_options': generate_options}
    if request.POST:
        context['player_name'] = player_name = request.POST['player-name']
        context['result'] = generate_dict[request.POST['to-generate']](player_name)
        context['to_generate'] = request.POST['to-generate']
    return render(request, 'battles/index.html', context)
