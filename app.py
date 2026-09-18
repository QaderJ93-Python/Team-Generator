import random
import streamlit as st

st.set_page_config(page_title="Balanced Team Generator", page_icon="⚖️", layout="centered")

# ----------------------------
# Session State
# ----------------------------
if "players" not in st.session_state:
    st.session_state.players = []

# ----------------------------
# Helpers
# ----------------------------
def add_player(name, skill, role):
    if name.strip():
        st.session_state.players.append({
            "name": name.strip(),
            "skill": int(skill),
            "role": role.strip() if role.strip() else "Any"
        })

def remove_player(index):
    if 0 <= index < len(st.session_state.players):
        del st.session_state.players[index]

def calculate_team_stats(team):
    total_skill = sum(player["skill"] for player in team)
    avg_skill = total_skill / len(team) if team else 0
    return total_skill, avg_skill

def generate_balanced_teams(players, num_teams):
    # Shuffle players lightly to add variety while preserving balance
    shuffled = players[:]
    random.shuffle(shuffled)

    # Sort by skill descending to assign strongest players first
    sorted_players = sorted(shuffled, key=lambda p: (p["skill"], random.random()), reverse=True)

    teams = [[] for _ in range(num_teams)]
    team_scores = [0] * num_teams
    team_counts = [0] * num_teams

    for player in sorted_players:
        # Pick the team with the lowest current total skill
        # Tie-breaker: fewer players, then random
        best_team = min(
            range(num_teams),
            key=lambda i: (
                team_scores[i],
                team_counts[i],
                random.random()
            )
        )
        teams[best_team].append(player)
        team_scores[best_team] += player["skill"]
        team_counts[best_team] += 1

    # Optional: rebalance by moving players if team sizes are uneven
    # This keeps the app simple and fair.
    return teams, team_scores

# ----------------------------
# Title
# ----------------------------
st.title("⚖️ Balanced Team Generator")

# ----------------------------
# Add Player Form
# ----------------------------
with st.form("player_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        name = st.text_input("Player Name")
    with col2:
        skill = st.number_input("Skill", min_value=1, max_value=10, value=5)
    with col3:
        role = st.text_input("Role (Optional)", placeholder="e.g. striker, defender, support")

    submitted = st.form_submit_button("Add Player")
    if submitted and name.strip():
        add_player(name, skill, role)
        st.success(f"Added {name.strip()}")

# ----------------------------
# Current Roster
# ----------------------------
st.subheader("Current Roster")

if st.session_state.players:
    for idx, player in enumerate(st.session_state.players):
        col_name, col_skill, col_role, col_remove = st.columns([2, 1, 2, 1])
        with col_name:
            st.write(player["name"])
        with col_skill:
            st.write(f"Skill: {player['skill']}")
        with col_role:
            st.write(f"Role: {player['role']}")
        with col_remove:
            if st.button("Remove", key=f"remove_{idx}"):
                remove_player(idx)
                st.rerun()

    st.markdown("---")

    col_clear, col_teams = st.columns([1, 3])
    with col_clear:
        if st.button("Clear Roster"):
            st.session_state.players = []
            st.rerun()

    with col_teams:
        num_teams = st.slider("Number of Teams", min_value=2, max_value=6, value=2)

    if st.button("Generate Teams", use_container_width=True):
        if len(st.session_state.players) < num_teams:
            st.warning("Add more players to generate enough teams.")
        else:
            teams, team_scores = generate_balanced_teams(st.session_state.players, num_teams)

            st.subheader("Generated Teams")

            # Show summary
            team_cols = st.columns(num_teams)
            for i, team in enumerate(teams):
                with team_cols[i]:
                    total_skill, avg_skill = calculate_team_stats(team)
                    st.info(f"**Team {i + 1}**")
                    st.write(f"Players: {len(team)}")
                    st.write(f"Total Skill: {total_skill}")
                    st.write(f"Average Skill: {avg_skill:.2f}")

                    if team:
                        for player in team:
                            st.write(f"- {player['name']} ({player['skill']})")
                    else:
                        st.write("- No players")

else:
    st.info("Add players to begin creating balanced teams.")
